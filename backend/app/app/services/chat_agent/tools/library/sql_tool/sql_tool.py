# -*- coding: utf-8 -*-
# mypy: disable-error-code="override"
from __future__ import annotations

import logging
import re
from typing import Any, List, Optional, Tuple

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.core.config import settings
from app.db.session import sql_tool_db
from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import SqlToolConfig, ToolInputSchema
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.helpers.query_formatting import standard_query_format
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool
from app.utils.sql import is_sql_query_safe

logger = logging.getLogger(__name__)


class SQLTool(ExtendedBaseTool):
    """SQL Tool."""

    name = "sql_tool"
    appendix_title = "Table Appendix"

    nb_example_rows: int = 3
    validate_empty_results: bool = False
    validate_with_llm: bool = False
    always_limit_query: bool = False

    @classmethod
    def from_config(
        cls,
        config: SqlToolConfig,
        common_config: AgentAndToolsConfig,
        **kwargs: Any,
    ) -> SQLTool:
        """Create a SQL tool from a config."""
        llm = kwargs.get(
            "llm",
            get_llm(common_config.llm),
        )
        fast_llm = kwargs.get(
            "fast_llm",
            get_llm(common_config.fast_llm),
        )
        fast_llm_token_limit = kwargs.get(
            "fast_llm_token_limit",
            common_config.fast_llm_token_limit,
        )

        SQLTool.check_init(warning=True)

        return cls(
            llm=llm,
            fast_llm=fast_llm,
            fast_llm_token_limit=fast_llm_token_limit,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_selection=(
                config.prompt_selection.format(**{e.name: e.content for e in config.prompt_inputs})
                if config.prompt_selection
                else None
            ),
            system_context_selection=(
                config.system_context_selection.format(**{e.name: e.content for e in config.prompt_inputs})
                if config.system_context_selection
                else None
            ),
            prompt_validation=(
                config.prompt_validation.format(**{e.name: e.content for e in config.prompt_inputs})
                if config.prompt_validation
                else None
            ),
            system_context_validation=(
                config.system_context_validation.format(**{e.name: e.content for e in config.prompt_inputs})
                if config.system_context_validation
                else None
            ),
            prompt_refinement=(
                config.prompt_refinement.format(**{e.name: e.content for e in config.prompt_inputs})
                if config.prompt_refinement
                else None
            ),
            nb_example_rows=config.nb_example_rows,
            validate_empty_results=config.validate_empty_results,
            validate_with_llm=config.validate_with_llm,
            always_limit_query=config.always_limit_query,
        )

    @staticmethod
    def check_init(warning: bool) -> None:
        if not settings.SQL_TOOL_DB_ENABLED:
            msg = (
                "The SQL Tool is not enabled. Please set the environment"
                " variables to enable it if used in the configuration."
            )
            if warning:
                logger.warning(msg)
            else:
                raise ValueError(msg)
        if sql_tool_db is None:
            msg = "Database is not initialized"
            if warning:
                logger.warning(msg)
            else:
                raise ValueError(msg)
        elif sql_tool_db.db_info is None:
            msg = "Database schema information is not initialized"
            if warning:
                logger.warning(msg)
            else:
                raise ValueError(msg)

    def _run(
        self,
        *args: Any,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError("Tool does not support sync")

    async def _arun(
        self,
        *args: Any,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> str:
        """Use the tool asynchronously.

        DISCLAIMER: Building Q&A systems of SQL databases requires executing model-
        generated SQL queries. There are inherent risks in doing this. Make sure
        that your database connection permissions are always scoped as narrowly
        as possible for your chain/agent's needs. This will mitigate though not
        eliminate the risks of building a model-driven system. For more on general
        security best practices, see https://python.langchain.com/v0.1/docs/security/
        """
        SQLTool.check_init(warning=False)

        query = kwargs.get(
            "query",
            args[0],
        )
        query = standard_query_format(ToolInputSchema.parse_raw(query))
        try:
            filtered_tables = await self._alist_sql_tables(
                query,
                run_manager,
            )
            (
                schemas,
                response,
            ) = await self._aquery_with_schemas(
                query,
                filtered_tables,
                run_manager,
            )

            result: str | None = None
            retries: int = 0
            is_valid = False

            if schemas == "":
                result = "no_data"

            while result is None:
                (
                    is_valid,
                    results_str,
                    complaints,
                ) = await self._avalidate_response(
                    query,
                    response,
                    run_manager,
                )
                if is_valid or retries > 3:
                    result = response
                else:
                    response = await self._aimprove_query(
                        query,
                        response,
                        complaints,
                        schemas,
                        run_manager,
                    )
                    retries += 1

            if run_manager is not None:
                if is_valid:
                    await run_manager.on_text(
                        result,
                        data_type=StreamingDataTypeEnum.APPENDIX,
                        tool=self.name,
                        step=1,
                        title=self.appendix_title,
                    )
                    return self._construct_final_response(
                        response,
                        results_str,
                    )
                await run_manager.on_text(
                    "no_data",
                    data_type=StreamingDataTypeEnum.ACTION,
                    tool=self.name,
                    step=1,
                    result=result,
                )
            return result
        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(
                    e,
                    tool=self.name,
                )
                return repr(e)
            raise e

    @staticmethod
    def _construct_final_response(
        markdown_sql_query: str,
        results_str: str,
    ) -> str:
        """Construct the final response."""
        return f"{markdown_sql_query}, {results_str}"

    async def _avalidate_response(
        self,
        question: str,
        response: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Tuple[bool, Any, Any]:
        """
        Validate the response.

        Returns:
            Tuple[bool, List[Any], str]: (is_valid, results_str, complaints)
        """
        try:
            query = await self._parse_query(response)
            if not is_sql_query_safe(query):
                return (
                    False,
                    [],
                    "The SQL query contains forbidden keywords (DML, DDL statements)",
                )
            if sql_tool_db is None:
                raise ValueError("Database is not initialized")
            results = sql_tool_db.run_no_str(query)
            if results is None:
                validation: Tuple[bool, Any, Any] = (
                    False,
                    [],
                    f"The SQL query did not return any results: {results}",
                )
            elif self.validate_empty_results and len(results) == 0:
                validation = (
                    False,
                    [],
                    "The SQL query executed but did not return any result rows.",
                )
            else:
                sample_rows_result = results[0 : self.nb_example_rows]
                sample_rows = list(
                    map(
                        lambda ls: [f"{str(i)[:100]}..." if len(str(i)) > 100 else str(i) for i in ls],
                        sample_rows_result,
                    )
                )
                sample_rows_str = ";".join([",".join(row) for row in sample_rows]).replace(
                    "\n",
                    "",
                )
                results_str = (
                    f"total rows from SQL query: {len(results)}, first {self.nb_example_rows} rows: {sample_rows_str}"
                )
                if self.validate_with_llm:
                    validation_messages = [
                        SystemMessage(content=self.system_context_validation or ""),
                        HumanMessage(
                            content=(
                                self.prompt_validation.format(
                                    query=response,
                                    result=results_str,
                                    question=question,
                                )
                                if self.prompt_validation
                                else ""
                            )
                        ),
                    ]
                    response = await self._agenerate_response(validation_messages)
                    validation = await self._parse_validation(response)
                else:
                    validation = (
                        True,
                        results_str,
                        None,
                    )
            logger.info(f"Validation: {validation} (success={validation[0]})")
            if run_manager is not None:
                await run_manager.on_text(
                    "validate_sql_query",
                    data_type=StreamingDataTypeEnum.ACTION,
                    tool=self.name,
                    step=1,
                    success=validation[0],
                )
            return validation
        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(
                    e,
                    tool=self.name,
                )
                return (
                    False,
                    [],
                    repr(e),
                )
            raise e

    async def _aimprove_query(
        self,
        query: str,
        response: str,
        complaints: str,
        schemas: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Improve the query async."""
        if run_manager is not None:
            await run_manager.on_text(
                "improve_sql_query",
                data_type=StreamingDataTypeEnum.ACTION,
                tool=self.name,
                step=1,
            )
        improvement_messages = [
            SystemMessage(content=self.system_context),
            HumanMessage(
                content=(
                    self.prompt_refinement.format(
                        previous_answer=response,
                        complaints=complaints,
                        table_schemas=schemas,
                        question=query,
                    )
                    if self.prompt_refinement
                    else ""
                )
            ),
        ]
        response = await self._agenerate_response(improvement_messages)
        return response

    async def _alist_sql_tables(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> List[str]:
        """List the SQL tables."""
        if run_manager is not None:
            await run_manager.on_text(
                "list_tables_sql_db",
                data_type=StreamingDataTypeEnum.ACTION,
                tool=self.name,
                step=1,
            )
        table_messages = [
            SystemMessage(content=self.system_context_selection if self.system_context_selection else ""),
            HumanMessage(content=self.prompt_selection.format(question=query) if self.prompt_selection else ""),
        ]
        response = await self._agenerate_response(
            table_messages,
            discard_fast_llm=True,
        )
        filtered_tables = [x.strip() for x in response.split(",")]
        logger.info(f"Filtered tables: {filtered_tables}")
        return filtered_tables

    async def _aquery_with_schemas(
        self,
        query: str,
        filtered_tables: List[str],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Tuple[str, str,]:
        """Query with schemas."""
        if run_manager is not None:
            await run_manager.on_text(
                "schema_sql_db",
                data_type=StreamingDataTypeEnum.ACTION,
                tool=self.name,
                step=1,
            )
        filtered_tables_upper_case = [x.upper() for x in filtered_tables]
        db_table_infos = sql_tool_db.db_info.tables if sql_tool_db and sql_tool_db.db_info is not None else []
        table_schemas = "\n".join(
            [
                ("DB.TABLE name: " + s.name + ", Table structure: " + s.structure)
                for s in db_table_infos
                if s.name.upper() in filtered_tables_upper_case
            ]
        )
        question_messages = [
            SystemMessage(content=self.system_context),
            HumanMessage(
                content=self.prompt_message.format(
                    table_schemas=table_schemas,
                    question=query,
                )
            ),
        ]
        response = await self._agenerate_response(
            question_messages,
            discard_fast_llm=True,
        )

        return (
            table_schemas,
            response,
        )

    @staticmethod
    async def _parse_validation(
        response: str,
    ) -> Tuple[bool, str, str,]:
        """Parse the validation from the response."""
        pattern = r"^Valid:\s*(?P<valid>yes|no)\s*Reason:\s*(?P<reason>.*)$"
        match = re.search(
            pattern,
            response,
            flags=re.MULTILINE,
        )

        return (
            ("y" in match.group("valid")) if match else False,
            "",
            match.group("reason") if match else response,
        )

    async def _parse_query(
        self,
        response: str,
    ) -> str:
        """Parse the query from the response."""
        response = response.replace(
            "\n",
            " ",
        ).replace(
            "\r",
            " ",
        )
        query_start = response.lower().find("```sql")
        if query_start == -1:
            query_start = response.lower().find("`sql")
        query_end = response.find(
            "```",
            query_start + 1,
        )
        if query_end == -1:
            query_end = response.find(
                "`",
                query_start + 1,
            )

        if query_start == -1 or query_end == -1:
            raise ValueError("Could not parse query from response")
        query = response[query_start + 6 : query_end]
        if self.always_limit_query and "LIMIT" not in query.upper():
            for i in range(3):
                if query[len(query) - 1 - i] == ";":
                    query = query[: -1 - i]
                    break
            query += f" LIMIT {self.nb_example_rows}"
        return query
