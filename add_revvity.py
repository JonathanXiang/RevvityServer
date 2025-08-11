from opcua import Server
from opcua import ua
import time
import json
from revvitywrapper import RevvityLiquidHandler


def add_revvity(ns_idx, parent, name: str = "RevvityHandler"):
    revvity_obj = parent.add_object(ns_idx, name)
    status_variable = revvity_obj.add_variable(ns_idx, "Status", "Initializing")

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
        return [ua.Variant(p, ua.VariantType.String) for p in protocols]
    
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
    
    def _count_tips_used(parent):
        result = handler.count_tips_used()
        if isinstance(result, dict) and "error" in result:
            status_variable.set_value(result["error"])
            return [ua.Variant(-1, ua.VariantType.Int32)]
        return [ua.Variant(result, ua.VariantType.Int32)]
    
    def _count_tips_available(parent):
        result = handler.count_tips_available()
        if isinstance(result, dict) and "error" in result:
            status_variable.set_value(result["error"])
            return [ua.Variant(-1, ua.VariantType.Int32)]
        return [ua.Variant(result, ua.VariantType.Int32)]
    
    revvity_obj.add_method(ns_idx, "UpdateStatus",     _update_status,     [], []).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "GetProtocols",     _get_protocols,     [], [ua.VariantType.String]).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "RunProtocol",     _run_protocol,     [ua.VariantType.String], []).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "GetParameters",     _get_parameters,     [], [ua.VariantType.String]).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "UpdateParameters",     _update_parameters,     [ua.VariantType.String], []).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "CountTipsUsed", _count_tips_used, [], [ua.VariantType.Int32]).set_modelling_rule(True)
    revvity_obj.add_method(ns_idx, "CountTipsAvailable", _count_tips_available, [], [ua.VariantType.Int32]).set_modelling_rule(True)

    return revvity_obj



    