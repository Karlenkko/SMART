import json

from flask import Blueprint
from flask import abort, request, jsonify
import hashlib
from blueprints.naiveBlockchain.format import format

naiveBlockchain_bp = Blueprint('naiveBlockchain', __name__)

filename = "blueprints/naiveBlockChain/naiveblockchain.txt"
lastblockfilename = "blueprints/naiveBlockChain/lastblock.txt"



class Block:
    index = 0
    previousHash = ""
    timestamp = ""
    data = ""
    hash = ""
    def __init__(self, index, previousHash, timestamp, data, hash):
        self.index = int(index)
        self.previousHash = str(previousHash)
        self.timestamp = str(timestamp)
        self.data = str(data)
        self.hash = str(hash)
    def toString(self):
        return str(self.index) + ";" + str(self.previousHash) + ";" + str(self.timestamp) + ";" + str(self.data) + ";" + str(self.hash)

genesisBlock = Block(0, "0", "1620068806", "Genesis Block", "e66a3ddf65e401ba40a3a908a8751a1306ae7c12999a2877a0f016582c53e975")

def calculateHashes(index, previousHash, timestamp, data):
    hash = hashlib.sha256()
    hash.update((str(index) + str(previousHash) + str(timestamp) + str(data)).encode(encoding="UTF-8"))

    return str(hash.hexdigest())

def calculateBlockHash(block):
    return calculateHashes(block.index, block.previousHash, block.timestamp, block.data)


def isValidNewBlock(newBlock, previousBlock):
    if not int(previousBlock.index) + 1 == int(newBlock.index):
        return False
    elif not str(previousBlock.hash) == str(newBlock.previousHash):
        return False
    elif not str(calculateBlockHash(newBlock)) == str(newBlock.hash):
        return False
    else:
        return True


def readLastBlock():
    lastf = open(lastblockfilename, 'r', encoding='UTF-8')
    lastline = lastf.readline()
    lastf.close()
    params = lastline.split(";")
    return Block(params[0], params[1], params[2], params[3], params[4])

def appendBlock(block):
    if isValidNewBlock(block, readLastBlock()):
        f = open(filename, 'a+', encoding='UTF-8')
        lastf = open(lastblockfilename, 'w', encoding='UTF-8')
        f.write(block.toString() + '\n')
        lastf.write(block.toString())
        f.close()
        lastf.close()
        return True
    else:
        return False


def readAllBlock():
    blocks = []
    f = open(filename, 'r', encoding='UTF-8')
    for line in f.readlines():
        line = line.strip()
        params = line.split(";")
        blocks.append(Block(params[0], params[1], params[2], params[3], params[4]))
    return blocks


def checkOrderVolunteer(orderId, selectedPerson, blocks):
    for block in blocks:
        data = block.data.split("|")
        if str(data[0]) == "1":
            if str(data[1]) == str(selectedPerson) and str(data[2]) == str(orderId):
                return True

    return False

@naiveBlockchain_bp.route('/blockchain/getLastBlock/', methods=['GET'])
def getLastBlock():
    res = {
        "status": "ok",
        "lastBlock": readLastBlock().toString()
    }
    return jsonify(res), 200

@naiveBlockchain_bp.route('/blockchain/addBlock/', methods=['POST'])
def addBlock():
    try:
        data = json.loads(request.get_data(as_text=True))
        hash = calculateHashes(str(data['block']['index']),str(data['block']['previousHash']),str(data['block']['timestamp']),str(data['block']['data']))
        block = Block(int(data['block']['index']),str(data['block']['previousHash']),str(data['block']['timestamp']),str(data['block']['data']),hash)
        flag = appendBlock(block)
        print(readLastBlock().toString())
        res = {}
        if flag:
            res = {
                "status": "added",
                "lastBlock": readLastBlock().toString()
            }
        else:
            res = {
                "status": "wrong block",
                "lastBlock": readLastBlock().toString()
            }
    except:
        abort(500)
    else:
        return jsonify(res), 201

@naiveBlockchain_bp.route('/blockchain/checkVolunteer/', methods=['GET'])
def checkVolunteer():
    if not request.args or not 'userId' in request.args or not 'orderId' in request.args:
        abort(400)
    else:
        try:
            blocks = readAllBlock()
            flag = checkOrderVolunteer(request.args.get('orderId'), request.args.get('userId'), blocks)
            if flag:
                res = {
                    "search" : "completed",
                    "volunteering" : "full participation"
                }
            else:
                res = {
                    "search": "completed",
                    "volunteering": "absence"
                }
        except:
            res = {
                "search": "aborted",
                "volunteering": ""
            }
            return jsonify(res), 200
        else:
            return jsonify(res), 200