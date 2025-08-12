from opcua import Server
from opcua import ua
import time
import json
from revvitywrapper import RevvityLiquidHandler
import os, re

COORD_RE = re.compile(r'([A-G])\s*([1-9])', re.IGNORECASE)

def add_revvity(ns_idx, parent, name: str = "RevvityHandler"):
    revvity_obj = parent.add_object(ns_idx, name)
    status_variable = revvity_obj.add_variable(ns_idx, "Status", "Initializing")
    tip_avail_var = revvity_obj.add_variable(ns_idx, "TipAvailability", "{}")

    handler = RevvityLiquidHandler()

    def _update_status(parent):
        status = handler.get_status()
        if isinstance(status, str):
            status_summary = status
        else:
            status_summary = (
                f"Running: {status.get('IsRunning', False)} | "
                f"Code: {status.get('StatusCode', 'Unknown')} | "
                f"Err: {status.get('ErrorCode', 'OK')} | "
                f"Msg: {status.get('ErrorMessage', '')}"
            )

        status_variable.set_value(status_summary)
        return []
    
    def _get_protocols(parent):
        protocols = handler.get_protocols()
        return [ua.Variant(protocols, ua.VariantType.String)]
    
    def _run_protocol(parent, protocol_variant):
        protocol = protocol_variant.Value
        result = handler.run_protocol(protocol)
        _update_status(parent)
        return []
    
    def _get_parameters(parent):
        parameters = handler.get_parameters()
        jsonstr = json.dumps(parameters)
        return [ua.Variant(jsonstr, ua.VariantType.String)]
    
    def _update_parameters(parent, json_variant):
        json_str = json_variant.Value
        param_dict = json.loads(json_str)
        handler.set_parameters(param_dict)
        status_variable.set_value("Parameters updated")
        return []
    
    def _get_tip_availability(_parent):
        return [tip_avail_var.get_value()]
    
    def _update_tip_availability(_parent):
        try:
            state = handler.refresh_tip_availability()
            tip_avail_var.set_value(json.dumps(state))
            status_variable.set_value(f"Updated tips from {handler.dt_folder}")
            return [True]
        except Exception as e:
            status_variable.set_value(f"UpdateTipAvailability error: {e}")
            return [False]
    
    revvity_obj.add_method(ns_idx, "UpdateStatus",     _update_status,     [], []).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "GetProtocols",     _get_protocols,     [], [ua.VariantType.String]).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "RunProtocol",     _run_protocol,     [ua.VariantType.String], []).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "GetParameters",     _get_parameters,     [], [ua.VariantType.String]).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "UpdateParameters",     _update_parameters,     [ua.VariantType.String], []).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "GetTipAvailability", _get_tip_availability, [], [ua.VariantType.String]).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "UpdateTipAvailability", _update_tip_availability, [], [ua.VariantType.Boolean]).set_modelling_rule(True)

    return revvity_obj



    