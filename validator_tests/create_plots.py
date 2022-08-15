import argparse

from powerful_benchmarker.utils.constants import add_default_args
from validator_tests.utils import create_main
from validator_tests.utils.constants import add_exp_group_args
from validator_tests.utils.plot_val_vs_acc import plot_val_vs_acc


def scatter(plots_folder, df, per_feature_layer):
    kwargs = {}
    if args.no_color:
        kwargs["c"] = None
    plot_val_vs_acc(
        df,
        plots_folder,
        per_adapter=args.per_adapter,
        per_feature_layer=per_feature_layer,
        validator_set=args.validator_set,
        src_threshold=args.src_threshold,
        adapter=args.adapter,
        **kwargs
    )


def fn1(*args):
    scatter(*args, per_feature_layer=True)


def fn2(*args):
    scatter(*args, per_feature_layer=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(allow_abbrev=False)
    add_default_args(parser, ["exp_folder"])
    add_exp_group_args(parser)
    create_main.add_main_args(parser)
    parser.add_argument("--output_folder", type=str, default="plots")
    parser.add_argument("--validator_set", nargs="+", type=str, default=None)
    parser.add_argument("--src_threshold", type=float)
    parser.add_argument("--no_color", action="store_true")
    parser.add_argument("--per_adapter", action="store_true")
    parser.add_argument("--adapter", type=str)
    args = parser.parse_args()
    create_main.main(args, fn1, fn2)
