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
                AuditLogPost("Errored",FatelError=f"{step.name}: {e}")
            except Exception as e:
                logging.error("Unexpected error: %s",e)
                SendDiscordError(ctx.serial, f"{step.name}: {e}")
                AuditLogPost("Errored",Exception=f"{step.name}: {e}")
        if ctx.errors:
            msg = "\n".join([err.Message for err in ctx.errors])
            fields = [asdict(d.Fields) for d in ctx.errors if d.Fields != None]
            SendDiscordError(f"{ctx.serial} Errors", msg, fields)
            AuditLogPost("Errored",fields)
        else:
            SendDiscordSuccess(f"{ctx.serial} Success", "No Errors Detected")
            AuditLogPost("Successful",Message="No Errors Detected",Children=ctx.Commodities)
