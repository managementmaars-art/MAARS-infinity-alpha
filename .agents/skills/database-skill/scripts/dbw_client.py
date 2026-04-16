
import json
import hashlib
import hmac
import datetime
import urllib.request
import urllib.error
import urllib.parse
import re
import base64
import os
from typing import Any, Dict, Optional

_SKILL_HEADERS = {"X-Volc-Dbw-Skill": "database-skill"}


class DBWClient:
    def __init__(
        self,
        region: Optional[str] = None,
        ak: Optional[str] = None,
        sk: Optional[str] = None,
        host: Optional[str] = None,
        instance_id: Optional[str] = None,
        database: Optional[str] = None,
    ):
        self.region = region or os.environ.get("VOLCENGINE_REGION", "cn-beijing")
        self.ak = ak or os.environ.get("VOLCENGINE_ACCESS_KEY")
        self.sk = sk or os.environ.get("VOLCENGINE_SECRET_KEY")
        self.host = host
        self.instance_id = instance_id or os.environ.get("VOLCENGINE_INSTANCE_ID")
        self.database = database or os.environ.get("VOLCENGINE_DATABASE")

        # APIG 鉴权（优先级高于 AK/SK）
        self.api_base = os.environ.get("ARK_SKILL_API_BASE")
        self.api_key = os.environ.get("ARK_SKILL_API_KEY")

        # Load from .env if still missing
        if (not self.api_base or not self.api_key) and (not self.ak or not self.sk):
            try:
                env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
                if os.path.exists(env_path):
                    env_vars = self._parse_env_file(env_path)
                    self.api_base = self.api_base or env_vars.get("ARK_SKILL_API_BASE")
                    self.api_key = self.api_key or env_vars.get("ARK_SKILL_API_KEY")
                    self.ak = self.ak or env_vars.get("VOLCENGINE_ACCESS_KEY")
                    self.sk = self.sk or env_vars.get("VOLCENGINE_SECRET_KEY")
                    self.region = env_vars.get("VOLCENGINE_REGION") or self.region
                    self.instance_id = self.instance_id or env_vars.get("VOLCENGINE_INSTANCE_ID")
                    self.database = self.database or env_vars.get("VOLCENGINE_DATABASE")
            except Exception:
                pass

    @staticmethod
    def _parse_env_file(path: str) -> Dict[str, str]:
        """解析 .env 文件，支持 export KEY="value" # comment 格式。"""
        result = {}
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # 去掉 export 前缀
                if line.startswith("export "):
                    line = line[7:]
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                # 去掉行内注释：先处理引号内的值，再去掉注释
                value = value.strip()
                if value.startswith('"') and '"' in value[1:]:
                    value = value[1:value.index('"', 1)]
                elif value.startswith("'") and "'" in value[1:]:
                    value = value[1:value.index("'", 1)]
                else:
                    # 无引号时，# 之前的部分是值
                    if "#" in value:
                        value = value[:value.index("#")]
                    value = value.strip()
                if value:
                    result[key] = value
        return result

    def _sign_request(
        self,
        ak: str,
        sk: str,
        region: str,
        service: str,
        method: str,
        uri: str,
        query_params: str,
        headers: Dict[str, str],
        body: str,
    ) -> str:
        canonical_headers = "\n".join([f"{k.lower()}:{v}" for k, v in sorted(headers.items())]) + "\n"
        signed_headers = ";".join([k.lower() for k in sorted(headers.keys())])
        hashed_payload = hashlib.sha256(body.encode("utf-8")).hexdigest()

        canonical_request = f"{method}\n{uri}\n{query_params}\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"

        date = headers["X-Date"]
        credential_scope = f"{date[:8]}/{region}/{service}/request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = f"HMAC-SHA256\n{date}\n{credential_scope}\n{hashed_canonical_request}"
        # print(f"DEBUG: StringToSign:\n{string_to_sign}")

        if not sk:
            raise ValueError("Secret Key (SK) is missing. Please check your .env file.")

        k_date = hmac.new(sk.encode("utf-8"), date[:8].encode("utf-8"), hashlib.sha256).digest()
        k_region = hmac.new(k_date, region.encode("utf-8"), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service.encode("utf-8"), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, "request".encode("utf-8"), hashlib.sha256).digest()
        signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        authorization = f"HMAC-SHA256 Credential={ak}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        return authorization

    def _convert_pascal_to_snake(self, data: Any) -> Any:
        """递归转换 PascalCase 为 snake_case（正确处理连续大写字母）"""
        if not isinstance(data, dict):
            if isinstance(data, list):
                return [self._convert_pascal_to_snake(item) for item in data]
            return data
        converted = {}
        for key, value in data.items():
            # 处理连续大写字母: DBEngineVersion -> db_engine_version
            snake_key = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", key)
            snake_key = re.sub(r"([a-z])([A-Z])", r"\1_\2", snake_key)
            snake_key = snake_key.lower()
            converted[snake_key] = self._convert_pascal_to_snake(value)
        return converted

    def _call_api(self, action: str, body_args: Dict[str, Any]) -> Dict[str, Any]:
        service = "dbw"
        method = "POST"

        # 构建请求体（PascalCase）
        body_dict = {}
        for k, v in body_args.items():
            if v is None:
                continue
            if k[0].isupper() and "_" not in k:
                body_dict[k] = v
            else:
                body_dict[self._pascal_case(k)] = v
        body = json.dumps(body_dict)

        use_apig = bool(self.api_base and self.api_key)
        use_aksk = bool(self.ak and self.sk)

        if not use_apig and not use_aksk:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
            raise ValueError(
                f"缺少火山引擎凭证，请在配置文件中补充：{env_path}\n"
                f"\n"
                f'export VOLCENGINE_ACCESS_KEY=""       # [必须] 火山引擎 Access Key\n'
                f'export VOLCENGINE_SECRET_KEY=""       # [必须] 火山引擎 Secret Key\n'
                f'export VOLCENGINE_REGION="cn-beijing" # [可选] 地域，默认 cn-beijing\n'
                f'export VOLCENGINE_INSTANCE_ID=""      # [可选] 数据库实例 ID\n'
                f'export VOLCENGINE_DATABASE=""         # [可选] 数据库名\n'
            )

        if use_apig:
            url, headers = self._build_apig_request(action, service)
        else:
            url, headers = self._build_aksk_request(action, service, method, body)
        return self._do_request(url, headers, body, method)

    def _build_apig_request(self, action: str, service: str) -> tuple:
        url = f"{self.api_base.rstrip('/')}/?Action={action}&Version=2018-01-01"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "ServiceName": service,
            **_SKILL_HEADERS,
        }
        return url, headers

    def _build_aksk_request(self, action: str, service: str, method: str, body: str) -> tuple:
        uri = "/"
        query_params = f"Action={action}&Version=2018-01-01"
        host = f"{service}.{self.region}.volcengineapi.com"
        url = f"https://{host}{uri}?{query_params}"

        now = datetime.datetime.utcnow()
        x_date = now.strftime("%Y%m%dT%H%M%SZ")

        headers = {
            "Host": host,
            "Content-Type": "application/json",
            "X-Date": x_date,
            **_SKILL_HEADERS,
        }
        authorization = self._sign_request(
            self.ak, self.sk, self.region, service, method, uri, query_params, headers, body
        )
        headers["Authorization"] = authorization
        return url, headers

    def _do_request(self, url: str, headers: Dict[str, str], body: str, method: str) -> Dict[str, Any]:
        req = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            msg = f"HTTP {e.code}: {error_body}"
            if e.code == 409 and "CreateSessionError" in error_body:
                msg += (
                    "\n\n💡 提示：CreateSessionError 通常意味着当前账号无权访问该实例，"
                    "或实例不可用。请确认：\n"
                    "  1. 实例状态是否为 Running\n"
                    "  2. 联系实例管理员在 DBW 控制台添加授权"
                )
            raise ValueError(msg)

        if "ResponseMetadata" in result:
            meta = result["ResponseMetadata"]
            request_id = meta.get("RequestId", "Unknown")
            if meta.get("Error"):
                raise ValueError(f"API Error: {meta['Error']} (RequestId: {request_id})")

        if "Result" in result:
            res = result["Result"]
            if isinstance(res, dict):
                if "Results" in res:
                    return res
                return self._convert_pascal_to_snake(res)
            return res
        elif "ResponseMetadata" in result:
            meta = result["ResponseMetadata"]
            if meta.get("Error"):
                raise ValueError(f"API Error: {meta['Error']}")

        return result

    def _pascal_case(self, s: str) -> str:
        components = s.split("_")
        return "".join(x.title() for x in components)

    def nl2sql(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("GenerateSQLFromNL", args)

    def execute_sql(self, args: Dict[str, Any]) -> Dict[str, Any]:
        result = self._call_api("ExecuteSQL", args)
        if isinstance(result, dict):
            if "Results" in result or "results" in result:
                return result
        return result

    def list_databases(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("ListDatabases", args)

    def list_tables(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("ListTables", args)

    def get_table_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("GetTableInfo", args)

    def create_dml_sql_change_ticket(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("CreateDmlSqlChangeTicket", args)

    def create_ddl_sql_change_ticket(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("CreateDdlSqlChangeTicket", args)

    def describe_tickets(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTickets", args)

    def describe_ticket_detail(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTicketDetail", args)

    def describe_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeWorkflow", args)

    def describe_slow_logs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeSlowLogs", args)

    def describe_aggregate_slow_logs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeAggregateSlowLogs", args)

    def describe_slow_log_time_series_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeSlowLogTimeSeriesStats", args)

    def describe_full_sql_detail(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeFullSQLDetail", args)

    def describe_instances(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeInstances", args)

    def get_metric_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("GetMetricData", args)

    def get_metric_items(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("GetMetricItems", args)

    def describe_table_metric(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTableMetric", args)

    def describe_dialog_infos(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeDialogInfos", args)

    def describe_snapshot_collection_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeInstanceDasSnapShotCollectionStatus", args)

    def describe_dialog_snapshots(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeDialogSnapshots", args)

    def describe_dialog_detail_snapshot(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeDialogDetailSnapshot", args)

    def kill_process(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("KillProcess", args)

    def describe_instance_nodes(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeInstanceNodes", args)

    def analyze_trx_and_lock(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("AnalyzeTrxAndLock", args)

    def describe_trx_and_lock_analysis_task_results(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTrxAndLockAnalysisTaskResults", args)

    def create_trx_export_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("CreateTrxExportTask", args)

    def describe_err_logs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeErrLogs", args)

    def describe_health_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeHealthSummary", args)

    def describe_table_space(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTableSpace", args)

    def describe_table_spaces(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTableSpaces", args)
