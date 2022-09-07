import json
import logging

from aiohttp import web

from ._response_headers import get_response_headers

logger = logging.getLogger(__name__)


def _format_error(err):
    formatted_error = {"type": "internal_error", "message": "Server internal"}

    if isinstance(err, Exception):
        formatted_error["message"] = str(err)

    return formatted_error


def _format_errors(errors):
    results = []
    for error in errors:
        results.append(_format_error(error))
    return results


class BadRequestError(Exception):
    pass


def prepare_response(_req, data, _ctx):
    headers = get_response_headers()
    return web.json_response(data, headers=headers, dumps=json.dumps)


async def _handle_query(req, query, query_vars, operation_name, context):
    try:
        if not operation_name:
            operation_name = None

        return await req.app["ttftt_engine"].execute(
            query=query,
            variables=query_vars,
            context=context,
            operation_name=operation_name,
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(e)
        return {"data": None, "errors": _format_errors([e])}


async def _get_params(req):
    if "query" not in req.query:
        raise BadRequestError('The mandatory "query" parameter is missing.')

    variables = None
    if "variables" in req.query and req.query["variables"] != "":
        try:
            variables = json.loads(req.query["variables"])
        except Exception:  # pylint: disable=broad-except
            raise BadRequestError(
                'The "variables" parameter is invalid. '
                "A JSON mapping is expected."
            )

    return (req.query["query"], variables, req.query.get("operationName"))


async def _post_json_params(req):
    try:
        req_content = await req.json(loads=json.loads)
    except Exception:  # pylint: disable=broad-except
        raise BadRequestError("Body should be a JSON object")

    if "query" not in req_content:
        raise BadRequestError('The mandatory "query" parameter is missing.')

    variables = None
    if "variables" in req_content and req_content["variables"] != "":
        variables = req_content["variables"]
        try:
            if isinstance(variables, str):
                variables = json.loads(variables)
        except Exception:  # pylint: disable=broad-except
            raise BadRequestError(
                'The "variables" parameter is invalid. '
                "A JSON mapping is expected."
            )

    return (req_content["query"], variables, req_content.get("operationName"))


def set_variables_from_part(file_field, variables, map, eager=False):
    file_name = file_field.name
    if file_name not in map:
        raise BadRequestError(f"Invalid multipart request: file field {file_name} not in mapping")
    dotpaths = map[file_name]
    for dotpath in dotpaths:
        if dotpath.count(".") == 1:
            groupname, varname = dotpath.split(".")
            if groupname != "variables":
                raise BadRequestError(f"Multipart request {file_name} must set a variable")
            variables[varname] = file_field  # do we need to read this into memory?
        elif dotpath.count(".") == 2:
            groupname, varname, varindex = dotpath.split(".")
            if groupname != "variables":
                raise BadRequestError(f"Multipart request {file_name} must set a variable")
            try:
                index = int(varindex)
            except Exception as err:
                raise BadRequestError(f"Multipart request {file_name} has invalid index") from err
            variables[varname][index] = file_field
        else:
            raise BadRequestError(f"Multipart request {file_name} must be a valid dotpath")

    return variables


async def _post_multipart_params(req):
    "See https://github.com/jaydenseric/graphql-multipart-request-spec"
    reader = await req.multipart()
    operations_part = await reader.next()
    if not operations_part:
        raise BadRequestError("Invalid multipart request: not enough parts")
    if operations_part.name != "operations":
        raise BadRequestError("Invalid multipart request: `operations` must be the first part")
    try:
        operations = await operations_part.json()
    except Exception:
        raise BadRequestError("Invalid multipart request: `operations` must be JSON")

    # validate operations
    if "query" not in operations:
        raise BadRequestError('The mandatory "query" parameter is missing.')
    if "variables" not in operations:
        raise BadRequestError('The mandatory "variables" parameter is missing.')
    variables = operations["variables"]
    if not isinstance(variables, dict):
        raise BadRequestError("Invalid multipart request: variables must be a mapping")

    map_part = await reader.next()
    if not map_part:
        raise BadRequestError("Invalid multipart request: not enough parts")
    if map_part.name != "map":
        raise BadRequestError("Invalid multipart request: `map` must be the second part")
    try:
        map = await map_part.json()
    except Exception:
        raise BadRequestError("Invalid multipart request: `map` must be JSON")

    # validate map
    for key, values in map.items():
        if not isinstance(values, list):
            raise BadRequestError(f"Invalid multipart request: `map` value for {key} must be an array")
        if not all(dotpath.count(".") in (1, 2) for dotpath in values):
            raise BadRequestError(f"Invalid multipart request: `map` value for {key} must be an array of dotpaths")

    # Now we need to create file-like objects and populate them into the
    # `variables` dict. But because we are reading data in a stream, that
    # means we need to eagerly read all the data into memory -- or almost all,
    # since we can leave the last part unread and let the application handle that.
    # If there's only one file, everything's fine!
    for _ in range(len(map) - 1):
        file_field = await reader.next()
        if not file_field:
            raise BadRequestError("Invalid multipart request: not enough parts")
        variables = set_variables_from_part(file_field, variables, map, eager=True)

    # the last one is not eager
    file_field = await reader.next()
    if not file_field:
        raise BadRequestError("Invalid multipart request: not enough parts")
    variables = set_variables_from_part(file_field, variables, map, eager=False)

    return (operations["query"], variables, operations.get("operationName"))


class Handlers:
    @staticmethod
    async def _handle(param_func, req, context_factory):
        context_factory_mgr = context_factory(req)

        async with context_factory_mgr as context:
            try:
                qry, qry_vars, oprn_name = await param_func(req)
                data = await _handle_query(
                    req, qry, qry_vars, oprn_name, context
                )
            except BadRequestError as e:
                data = {"data": None, "errors": _format_errors([e])}

            return req.app["response_formatter"](req, data, context)

    @staticmethod
    async def handle_get(req, context_factory):
        return await Handlers._handle(_get_params, req, context_factory)

    @staticmethod
    async def handle_post(req, context_factory):
        if req.content_type == 'multipart/form-data':
            return await Handlers._handle(_post_multipart_params, req, context_factory)
        return await Handlers._handle(_post_json_params, req, context_factory)
