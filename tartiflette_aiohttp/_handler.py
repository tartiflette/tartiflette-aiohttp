import json
import logging

from aiohttp import web


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


def prepare_response(data):
    headers = {}
    # TODO Do things with header here
    return web.json_response(data, headers=headers, dumps=json.dumps)


async def _handle_query(req, query, query_vars, _query_name, context):
    try:
        return await req.app["ttftt_engine"].execute(
            query=query, variables=query_vars, context=context
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


async def _post_params(req):
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


class Handlers:
    @staticmethod
    async def _handle(param_func, user_c, req):
        user_c["req"] = req

        try:
            qry, qry_vars, qry_name = await param_func(req)
            return prepare_response(
                await _handle_query(req, qry, qry_vars, qry_name, user_c)
            )
        except BadRequestError as e:
            return prepare_response(
                {"data": None, "errors": _format_errors([e])}
            )

    @staticmethod
    async def handle_get(user_context, req):
        return await Handlers._handle(_get_params, user_context, req)

    @staticmethod
    async def handle_post(user_context, req):
        return await Handlers._handle(_post_params, user_context, req)
