from hashids import Hashids
import time

def hashid(length=4):
	hashids = Hashids(salt=str(time.time()), min_length=length, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
	return hashids.encode(int(time.time()))

if __name__ == '__main__':
	print hashid()
