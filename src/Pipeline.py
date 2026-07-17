from Context import Step,Context,FatalError
import logging
from Utilities.discord_noitification import *
from dataclasses import asdict

class Pipeline:
    def __init__(self,steps:list[Step]):
        self.steps:list[Step] = steps
        
    def run(self, ctx:Context):
        for step in self.steps:
            logging.info("Running Step: %s",step.name)
            try:
                step.run(ctx)
            except FatalError as e:
                logging.error("FatalError: %s",e)
                SendDiscordError(ctx.serial, f"{step.name}: {e}")
                return
        if ctx.errors:
            msg = "\n".join([err.Message for err in ctx.errors])
            fields = [asdict(d.Fields) for d in ctx.errors]
            SendDiscordError(f"{ctx.serial} Errors", msg, fields)
        else:
            SendDiscordSuccess(f"{ctx.serial} Success", "No Errors Detected")
