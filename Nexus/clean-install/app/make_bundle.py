import argparse
from bundle import create_bundle
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('destination');a=p.parse_args()
    print(create_bundle(a.manifest,a.destination))
