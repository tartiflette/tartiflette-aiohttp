# [Next]

## Added

- [ISSUE-55](https://github.com/tartiflette/tartiflette-aiohttp/issues/55) - Add
a new optional `context_factory` parameter to the `register_graphql_handlers`
function. This parameter can take a coroutine function which will be called on
each request with the following signature:
    ```python
    async def context_factory(
        req: "aiohttp.web.Request", context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates a new context.
        :param req: the incoming aiohttp request instance
        :param context: the value filled in through the `executor_context` parameter
        :type req: aiohttp.web.Request
        :type context: Dict[str, Any]
        :return: the context for the incoming request
        :rtype: Dict[str, Any]
        """
    ```

The aim of this function will be to returns the context which will be forwarded
to the Tartiflette engine on the `execute` or `subscribe` method.

## Changed

## Fixed