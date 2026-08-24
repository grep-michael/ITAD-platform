from Context import Step,Context,FatalError
import logging
from Utilities.status_handler import *
from dataclasses import asdict

class Pipeline:
    def __init__(self,steps:list[Step]):
        self.steps:list[Step] = steps
        
    def run(self, ctx:Context):
        AuditLogPost("Started")
        for step in self.steps:
            logging.info("Running Step: %s",step.name)
            try:
                step.run(ctx)
            except FatalError as e:
                logging.error("FatalError: %s",e)
                SendDiscordError(ctx.serial, f"{step.name}: {e}")
                AuditLogPost("Errored",FatalError=f"{step.name}: {e}")
                break
            except Exception as e:
                logging.error("Unexpected error: %s",e)
                SendDiscordError(ctx.serial, f"{step.name}: {e}")
                AuditLogPost("Errored",Exception=f"{step.name}: {e}")
        if ctx.errors:
            errors = {}
            for err in ctx.errors:
                errors[err.Message] = [asdict(f) for f in err.Fields]
            msg = "\n".join([err.Message for err in ctx.errors])
            fields = [asdict(f) for err in ctx.errors for f in err.Fields]
            SendDiscordError(f"{ctx.serial} Errors", msg, fields)
            AuditLogPost("Errored",Errors=errors)
        else:
            SendDiscordSuccess(f"{ctx.serial} Success", "No Errors Detected")
            print(ctx.Commodities)
            AuditLogPost("Successful",Message="No Errors Detected",**ctx.CommodityDict())
