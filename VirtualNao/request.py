import requests
import sys

def main():
	res = requests.get(sys.argv[1])
	print(res)
    # print(60)


if __name__ == '__main__':
	main()