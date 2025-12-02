from typing import List
from pydantic import BaseModel, Field


class FlowAlarmDetailItem(BaseModel):
    flow_alarm_detail_dst_ip: str = Field(default="")
    flow_alarm_detail_source_port: int = Field(default=0)
    flow_alarm_detail_source_ip: str = Field(default="")
    flow_alarm_detail_dst_port: int = Field(default=0)
    flow_alarm_detail_alarm_time: str = Field(default="")
    flow_alarm_detail_payload: str = Field(default="")


class FlowRiskAssetsItem(BaseModel):
    flow_risk_assets_risk_assets: str = Field(default="")
    flow_risk_assets_risk_type: str = Field(default="")
    flow_risk_assets_start_time: str = Field(default="")
    flow_risk_assets_risk_info: str = Field(default="")
    flow_risk_assets_update_time: str = Field(default="")


class HoneypotTimeAxisItem(BaseModel):
    honeypot_time_axis_honeypot_ip: str = Field(default="")
    honeypot_time_axis_detail_content: str = Field(default="")
    honeypot_time_axis_honeypot_port: int = Field(default=0)
    honeypot_time_axis_attack_ip: str = Field(default="")
    honeypot_time_axis_attack_port: int = Field(default=0)
    honeypot_time_axis_start_time: str = Field(default="")


class HostSecurityEventItem(BaseModel):
    host_security_event_host_ip: str = Field(default="")
    host_security_event_check_item: str = Field(default="")
    host_security_event_risk_level: str = Field(default="")
    host_security_event_alert_name: str = Field(default="")
    host_security_event_alert_time: str = Field(default="")
    host_security_event_detect_infos: str = Field(default="")


class SecurityEventData(BaseModel):
    flowAlarmDetail: List[FlowAlarmDetailItem] = Field(default_factory=list)
    flowRiskAssets: List[FlowRiskAssetsItem] = Field(default_factory=list)
    honeypotTimeAxis: List[HoneypotTimeAxisItem] = Field(default_factory=list)
    hostSecurityEvent: List[HostSecurityEventItem] = Field(default_factory=list)


class AlertRequest(BaseModel):
    sourceIp: str
    sourcePort: int
    dstIp: str
    dstPort: int
    payload: str = Field(default="")
    alarmTime: str


class AnalyzeRequest(BaseModel):
    alerts: SecurityEventData


class BatchAlertRequest(BaseModel):
    alerts: List[AlertRequest]


class BatchAnalyzeRequest(BaseModel):
    alerts: List[SecurityEventData]