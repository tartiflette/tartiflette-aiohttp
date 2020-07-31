import json
import logging

from aiohttp import web

from ._reponse_headers import get_response_headers

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
        return await Handlers._handle(_post_params, req, context_factory)
