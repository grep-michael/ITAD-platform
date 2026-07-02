import atexit, base64, gzip, os, shutil, subprocess, time, tempfile,logging
from _mvcli_data import BLOBS


def extract():
    d = tempfile.mkdtemp(prefix="mvcli_")
    atexit.register(shutil.rmtree, d, ignore_errors=True)
    for name, blob in BLOBS.items():
        path = os.path.join(d, name)
        with open(path, "wb") as f:
            f.write(gzip.decompress(base64.b64decode(blob)))
        os.chmod(path, 755)
    return d

def RemoveMarvellRaid():
    
    parentDir = extract()
    env = {**os.environ, "LD_LIBRARY_PATH": parentDir + ":" + os.environ.get("LD_LIBRARY_PATH", "")}
    logging.info("executing marvell raid removal")
    logging.info(f"List before removal: \n\t{os.listdir("/sys/block")}\n")
    for i in range(4):
        cmd = [os.path.join(parentDir,"mvcli"),"delete","-o","vd","-i",i,"--waiveconfirmation"]
        ret = subprocess.run(
            cmd,
            env=env)
        logging.info(" ".join(cmd))
        logging.info(ret)
    logging.info("Finished, sleeping for 30 seconds")
    time.sleep(30)
    logging.info(f"List after removal: \n\t{os.listdir("/sys/block")}\n")


if __name__ == "__main__":
    RemoveMarvellRaid()

