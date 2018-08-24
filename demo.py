import csv
import json
import os
import sys, getopt
import time
from collections import namedtuple
from ontology.common.address import Address
from ontology.ont_sdk import OntologySdk
from ontology.smart_contract.neo_contract.abi.abi_info import AbiInfo
from ontology.wallet.wallet_manager import WalletManager


def main(argv):
   try:
      opts, args = getopt.getopt(argv, "hm:i:f:", ["migrate=", "invoke=", "function"])
   except getopt.GetoptError:
      print('test.py [-m|--migrate] [-i|--invoke] ')
      sys.exit(2)
   m = {}
   for opt, arg in opts:
      if opt == '-h':
         print('test.py [-m|--migrate] [-i|--invoke invoke.json -f function] ')
         sys.exit()
      elif opt in ("-m", "--migrate"):
          m["func"] = "migrate"
          deploy_cmd(m, str(arg))
      elif opt in ("-i", "--invoke"):
         m["func"] = "invoke"
         invoke_cmd(m, str(arg))
      elif opt in ("-f", "--function"):
          funcs = str(arg).split(",")
          funcs2 = funcs.copy()
          for func in m["function"]:
              if func.function_name in funcs2:
                  funcs2.remove(func.function_name)
          if len(funcs2) == 0:
              execute(m, funcs)
          else:
              print("there is not the function:", funcs2)
          sys.exit()
   execute(m)


def deploy_cmd(m: [], arg: str):
    if "json" in str(arg):
        with open(arg, "r") as f:
            r = json.load(f, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            m["No"] = 1
            m["rpc_address"] = r.rpc_address
            m["need_storage"] = r.need_storage
            m["name"] = r.name
            m["code_version"] = r.code_version
            m["author"] = r.author
            m["email"] = r.email
            m["desp"] = r.desp
            m["payer_address"] = r.payer_address
            m["payer_password"] = r.payer_password
            m["wallet_file_path"] = r.wallet_file_path
            m["gas_limit"] = r.gas_limit
            m["gas_price"] = r.gas_price
            m["save_file"] = r.save_file
            if ".avm" in r.code:
                with open(r.code, "r") as f2:
                    m["code"] = f2.read()
            else:
                m["code"] = r.code
            m["contract_address"] = Address.address_from_vm_code(m["code"]).to_reverse_hex_str()
    else:
        temp = str(arg).split(",")
        m["No"] = 1
        for i in temp:
            t = str(i).split("=")
            m[t[0]] = t[1]


def invoke_cmd(m: [], arg: str):
    if "json" in str(arg):
        with open(arg, "r") as f:
            r = json.load(f, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            m["rpc_address"] = r.rpc_address
            m["payer_address"] = r.payer_address
            m["payer_password"] = r.payer_password
            m["wallet_file_path"] = r.wallet_file_path
            m["gas_limit"] = r.gas_limit
            m["gas_price"] = r.gas_price
            m["abi_path"] = r.abi_path
            m["save_file"] = r.save_file
            m["function"] = r.function
    else:
        temp = str(arg).split(",")
        for i in temp:
            t = str(i).split("=")
            m[t[0]] = t[1]


def execute(m:[], function_name=None):
    sdk = OntologySdk()
    sdk.set_rpc(m["rpc_address"])
    if m["func"] is "migrate":
        # 判断是否已经部署
        code = sdk.rpc.get_smart_contract(m["contract_address"])
        if code != "unknow contract":
            print("contract have been deployed")
            print("contract_address:", m["contract_address"])
            return
        need_storage = False
        if m["need_storage"] is 'true':
            need_storage = True
        tx = sdk.neo_vm().make_deploy_transaction(m["code"], need_storage, m["name"], m["code_version"], m["author"]
                                                  , m["email"], m["desp"], m["payer_address"], m["gas_limit"],
                                                  m["gas_price"])
        sdk.wallet_manager.open_wallet(m["wallet_file_path"])
        acct = sdk.wallet_manager.get_account(m["payer_address"], m["payer_password"])
        sdk.sign_transaction(tx, acct)
        sdk.set_rpc(m["rpc_address"])
        try:
            print("deploying，please waiting ...")
            res = sdk.rpc.send_raw_transaction(tx)
            print("txhash:", res)
            for i in range(10):
                time.sleep(1)
                res = sdk.rpc.get_smart_contract(m["contract_address"])
                if res == "unknow contract" or res == "":
                    continue
                else:
                    print("deploy success")
                    save_file(m, "success")
                    return
            print("deployed failed")
            save_file(m, "deployed failed")
        except Exception as e:
            print(e)
            save_file(m, e)

    elif m["func"] is "invoke":
        func_maps = {}
        for i in list(m["function"]):
            func_map = {}
            param_list = []
            func_map["function_name"] = i.function_name
            func_map["pre_exec"] = i.pre_exec
            try:
                for j in list(i.function_param):
                    param_list.append(j)
                func_map["param_list"] = param_list
            except Exception as e:
                pass
            if not i.pre_exec:
                try:
                    func_map["signers"] = i.signers
                except AttributeError as e:
                    func_map["signers"] = None
            func_maps[i.function_name] = func_map
        with open(str(m["abi_path"]), "r") as f:
            abi = json.loads(f.read(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            abi_info = AbiInfo(abi.hash, abi.entrypoint, abi.functions, abi.events)
            contract_address = bytearray.fromhex(str(abi.hash)[2:])
            m["contract_address"] = contract_address.hex()
            contract_address.reverse()
            sdk.wallet_manager.open_wallet(m["wallet_file_path"])
            payer = sdk.wallet_manager.get_account(m["payer_address"], m["payer_password"])
            func_l = []
            no = 0
            for func_map in func_maps.values():
                if function_name is not None:
                    if func_map["function_name"] not in function_name:
                        continue
                func = abi_info.get_function(func_map["function_name"])
                func_map["return_type"] = func.return_type
                params = []
                l = []
                l.append(no)
                no = no + 1
                l.append(func_map["function_name"])
                l.append(func_map["pre_exec"])
                temp_l = ""  # 用来放参数
                for i in range(len(func_map["param_list"])):
                    if type(func_map["param_list"][i]) is int:
                        temp_l += str(func_map["param_list"][i]) + ":"
                    else:
                        temp_l += func_map["param_list"][i] + ":"
                    if func.parameters[i].type == "String":
                        params.append(str(func_map["param_list"][i]))
                    if func.parameters[i].type == "ByteArray":
                        if func_map["param_list"][i].startswith("A"):
                            params.append(Address.b58decode(func_map["param_list"][i], False).to_array())
                        else:
                            params.append(bytearray(func_map["param_list"][i].encode()))
                    if func.parameters[i].type == "Integer":
                        params.append(func_map["param_list"][i])
                l.append(temp_l[:len(temp_l) - 1])
                if len(params) == 1:
                    func.set_params_value(params[0])
                elif len(params) == 2:
                    func.set_params_value(params[0], params[1])
                elif len(params) == 3:
                    func.set_params_value(params[0], params[1], params[2])
                elif len(params) == 4:
                    func.set_params_value(params[0], params[1], params[2], params[3])
                elif len(params) == 5:
                    func.set_params_value(params[0], params[1], params[2], params[3], params[4])
                elif len(params) == 6:
                    func.set_params_value(params[0], params[1], params[2], params[3], params[4], params[5])
                elif len(params) == 7:
                    func.set_params_value(params[0], params[1], params[2], params[3], params[4], params[5], params[6])

                try:
                    print("")
                    print("invoking, please waiting ...")
                    print("method: " + func_map["function_name"])
                    if func_map["pre_exec"]:
                        res = sdk.neo_vm().send_transaction(contract_address, None, None, 0,
                                                            0, func, True)
                        if res["error"] != 0:
                            print(res["desc"])
                            l.append(res["desc"])
                        else:
                            if res["result"]["Result"] == None or res["result"]["Result"] == "":
                                print("res:", res["result"]["Result"])
                                l.append("")
                            else:
                                if func_map["return_type"] == "Integer":
                                    value = bytearray.fromhex(res["result"]["Result"])
                                    value.reverse()
                                    print("res:", int(value.hex(), 16))
                                    l.append(int(value.hex(), 16))
                                else:
                                    print("res:", (bytearray.fromhex(res["result"]["Result"])).decode('utf-8'))
                                    l.append((bytearray.fromhex(res["result"]["Result"])).decode('utf-8'))
                    else:
                        res = ""
                        if func_map["signers"] != None:
                            wm = WalletManager()
                            wm.open_wallet(func_map["signers"].signer.walletpath)
                            signer = wm.get_account(func_map["signers"].signer.address,
                                                                    func_map["signers"].signer.password)
                            res = sdk.neo_vm().send_transaction(contract_address, signer, payer, m["gas_limit"],
                                                                m["gas_price"], func, False)
                        else:
                            res = sdk.neo_vm().send_transaction(contract_address, payer, payer, m["gas_limit"],
                                                                m["gas_price"], func, False)
                        for i in range(10):
                            time.sleep(1)
                            event = sdk.rpc.get_smart_contract_event_by_tx_hash(res)
                            if event != None:
                                print("txhash:", res)
                                print("event:", event)
                                break
                        l.append(res)
                except Exception as e:
                    print("Error:", e)
                    l.append(e)
                func_l.append(l)
            save_file(m, "", func_l)
    else:
        print("only support migrate and invoke")


def save_file(m: [], res: str, func_l = None):
    ishasheader = False
    no = 0
    print(m["save_file"])
    if os.path.exists(m["save_file"]):
        with open(m["save_file"], "r") as f:
            lines = list(csv.reader(f))
            if len(lines) == 0:
                no = 0
            else:
                ishasheader = True
                line = list(lines)[len(list(lines)) - 1]
                no = int(line[0], 10) + 1
    if m["func"] == "migrate":
        with open(m["save_file"], "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if not ishasheader:
                writer.writerow(
                    ["No","need_storage", "name", "code_version", "author", "email", "desp", "payer_address", "gas_limit",
                     "gas_price"])
            writer.writerow([m["No"]+no, m["need_storage"], m["name"], m["code_version"], m["author"], m["email"], m["desp"],
                             m["payer_address"], m["gas_limit"], m["gas_price"], res])
    elif m["func"] == "invoke":
        with open(m["save_file"], "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if not ishasheader:
                writer.writerow(["No", "contract_address", "payer_address", "gas_limit", "gas_price","function_name","pre_exec","params", "result"])
            for i in func_l:
                writer.writerow([i[0]+no, m["contract_address"], m["payer_address"], m["gas_limit"], m["gas_price"],i[1], i[2], i[3],i[4]])


if __name__ == "__main__":
   main(sys.argv[1:])