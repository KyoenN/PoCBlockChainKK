import datetime
import hashlib
import random
import time
import multiprocessing


class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash, nonce):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash
        self.nonce = nonce


def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()


def isblockvalid(block_data, hash, difficulty, nonce, process_index, result_queue):
    if hash.startswith('0' * difficulty):
        result_queue.put((nonce, hash, process_index))
        return True
    return False


def mine_block(index, previous_hash, data, difficulty, start_nonce, end_nonce, process_index, result_queue):
    for nonce in range(start_nonce, end_nonce):
        block_data = f'{index}{previous_hash}{data}{nonce}'
        block_hash = sha256(block_data)
        if isblockvalid(block_data, block_hash, difficulty, nonce, process_index, result_queue):
            break


def mine_blocks(index, previous_hash, data, difficulty, num_processes):
    result_queue = multiprocessing.Queue()

    processes = []
    for i in range(num_processes):
        start_nonce = i * (2 ** 32) // num_processes
        end_nonce = (start_nonce + (2 ** 32) // num_processes) - 1

        process = multiprocessing.Process(target=mine_block, args=(
            index, previous_hash, data, difficulty, start_nonce, end_nonce, i, result_queue))
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    results = [result_queue.get() for _ in range(num_processes)]
    print(f'{results}\n')

    nonce, block_hash, process_index = min(results, key=lambda x: int(x[1], 16))

    print(f"Process {process_index} found the correct nonce first\n")

    return nonce, block_hash


def main():
    difficulty = 5
    num_blocks = random.randint(10, 50)
    previous_hash = '0'

    blockchain = [Block(0, '0', time.time(), 'Genesis Block', sha256('Genesis Block'), 0)]

    for i in range(1, num_blocks):
        timestamp = time.time()
        date = datetime.datetime.fromtimestamp(timestamp)
        data = f'Block {i} Data'

        nonce, block_hash = mine_blocks(i, previous_hash, data, difficulty, num_processes=10)

        block = Block(i, previous_hash, timestamp, data, block_hash, nonce)
        blockchain.append(block)

        print(
            f"Block {i} mined with hash: {block_hash} and nonce: {nonce}, previous block was: {previous_hash}, the block was mined at: {date},\n")

        previous_hash = block_hash


if __name__ == "__main__":
    main()
