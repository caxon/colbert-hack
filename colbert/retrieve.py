import os
import random
import sys

from colbert.utils.parser import Arguments
from colbert.utils.runs import Run

from colbert.evaluation.loaders import load_colbert, load_qrels, load_queries
from colbert.indexing.faiss import get_faiss_index_name
from colbert.ranking.retrieval import retrieve
from colbert.ranking.batch_retrieval import batch_retrieve

from collections import OrderedDict

# inject custom args
custom_args = [
    '--nprobe', '32',
    '--partitions', '3000',
    '--faiss_depth', '64',
    '--index_root', './indexes/',
    '--index_name', 'WWII.default',
    '--doc_maxlen', '180',
    '--mask-punctuation',
    '--bsize', '256',
    '--amp',
    '--checkpoint', './data/msmarco-doc-2020oct04-colbert-200k.dnn',
    '--root', './experiments/',
    '--queries', './data/queries.dev.1.tsv'
    ]

def main():
    print("SYS ARGS", sys.argv)

    random.seed(12345)

    parser = Arguments(description='End-to-end retrieval and ranking with ColBERT.')

    parser.add_model_parameters()
    parser.add_model_inference_parameters()
    parser.add_ranking_input()
    parser.add_retrieval_input()

    parser.add_argument('--faiss_name', dest='faiss_name', default=None, type=str)
    parser.add_argument('--faiss_depth', dest='faiss_depth', default=1024, type=int)
    parser.add_argument('--part-range', dest='part_range', default=None, type=str)
    parser.add_argument('--batch', dest='batch', default=False, action='store_true')
    parser.add_argument('--depth', dest='depth', default=1000, type=int)

    # args = parser.parse()
    args = parser.parse(custom_args)


    args.depth = args.depth if args.depth > 0 else None

    if args.part_range:
        part_offset, part_endpos = map(int, args.part_range.split('..'))
        args.part_range = range(part_offset, part_endpos)

    with Run.context():
        args.colbert, args.checkpoint = load_colbert(args)
        args.qrels = load_qrels(args.qrels)
        # args.queries = load_queries(args.queries)
        args.queries = OrderedDict([(0, "how do I play sports")])

        args.index_path = os.path.join(args.index_root, args.index_name)

        if args.faiss_name is not None:
            args.faiss_index_path = os.path.join(args.index_path, args.faiss_name)
        else:
            args.faiss_index_path = os.path.join(args.index_path, get_faiss_index_name(args))

        #####--------#####
        
        print(f"ARGS: {dir(args)}\n-------------\n")
        print("QUERIES", args.queries)
        print("AMP", args.amp)
        print("DEPTH", args.depth)
        print("BATCH", args.batch)
        print("PART_RANGE", args.part_range)
        print("FAISS_DEPTH", args.faiss_depth)
        print("FAISS_NAME", args.faiss_depth)

        #####--------#####

        if args.batch:
            batch_retrieve(args)
        else:
            retrieve(args)

global_args = None

### Call this before any api usage

def init_retrieve():
    print("Initiated retrieve!")

    random.seed(12345)

    parser = Arguments(description='End-to-end retrieval and ranking with ColBERT.')

    parser.add_model_parameters()
    parser.add_model_inference_parameters()
    parser.add_ranking_input()
    parser.add_retrieval_input()

    parser.add_argument('--faiss_name', dest='faiss_name', default=None, type=str)
    parser.add_argument('--faiss_depth', dest='faiss_depth', default=1024, type=int)
    parser.add_argument('--part-range', dest='part_range', default=None, type=str)
    parser.add_argument('--batch', dest='batch', default=False, action='store_true')
    parser.add_argument('--depth', dest='depth', default=1000, type=int)

    args = parser.parse(custom_args)

    args.depth = args.depth if args.depth > 0 else None

    if args.part_range:
        part_offset, part_endpos = map(int, args.part_range.split('..'))
        args.part_range = range(part_offset, part_endpos)

    args.colbert, args.checkpoint = load_colbert(args)
    args.qrels = load_qrels(args.qrels)

    args.index_path = os.path.join(args.index_root, args.index_name)

    if args.faiss_name is not None:
        args.faiss_index_path = os.path.join(args.index_path, args.faiss_name)
    else:
        args.faiss_index_path = os.path.join(args.index_path, get_faiss_index_name(args))

    global global_args
    global_args = args


### Call this every time you have a query
def retrieve_query(query: str):
    # load static global args
    args = global_args

    # with Run.context():
    args.queries = OrderedDict([(0, query)])

    return retrieve(args)

if __name__ == "__main__":
    main()