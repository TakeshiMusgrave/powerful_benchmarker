import json

import numpy as np

from .utils import dict_to_str, validator_str

SPLIT_NAMES = ["src_train", "src_val", "target_train", "target_val"]
AVERAGE_NAMES = ["micro", "macro"]


def exp_specific_columns(df, additional_exclude=None, exclude=None):
    if exclude is None:
        exclude = ["score", "validator", "validator_args"]
        if additional_exclude:
            exclude.extend(additional_exclude)
    return [x for x in df.columns.values if x not in exclude]


def acc_score_column_name(split, average):
    return f"{split}_{average}"


def all_acc_score_column_names():
    return [acc_score_column_name(x, y) for x in SPLIT_NAMES for y in AVERAGE_NAMES]


def get_acc_rows(df, split, average):
    args = dict_to_str({"average": average, "split": split})
    return df[(df["validator_args"] == args) & (df["validator"] == "Accuracy")]


def drop_validator_cols(df, drop_validator_args=True):
    cols = ["validator"]
    if drop_validator_args:
        cols.append("validator_args")
    return df.drop(columns=cols)


def get_acc_df(df, split, average):
    df = get_acc_rows(df, split, average)
    df = drop_validator_cols(df)
    return df.rename(columns={"score": acc_score_column_name(split, average)})


def get_all_acc(df):
    output = None
    for split in SPLIT_NAMES:
        for average in ["micro", "macro"]:
            curr = get_acc_df(df, split, average)
            if output is None:
                output = curr
            else:
                output = output.merge(
                    curr, on=exp_specific_columns(output, all_acc_score_column_names())
                )
    return output


# need to do this to avoid pd hash error
def convert_list_to_tuple(df):
    df.src_domains = df.src_domains.apply(tuple)
    df.target_domains = df.target_domains.apply(tuple)


def assert_acc_rows_are_correct(df):
    # make sure score and split/average columns are equal
    for split in SPLIT_NAMES:
        for average in ["micro", "macro"]:
            curr = get_acc_rows(df, split, average)
            if not curr["score"].equals(curr[acc_score_column_name(split, average)]):
                raise ValueError("These columns should be equal")


def drop_irrelevant_columns(df):
    return df.drop(
        columns=[
            "exp_folder",
            "dataset_folder",
            "num_workers",
            "evaluate",
            "save_features",
            "download_datasets",
            "use_stat_getter",
            "check_initial_score",
            "use_full_inference",
            "exp_validator",
        ]
    )


def domains_str(domains):
    return "_".join(domains)


def task_str(dataset, src_domains, target_domains):
    return f"{dataset}_{domains_str(src_domains)}_{domains_str(target_domains)}"


def add_task_column(df):
    new_col = df.apply(
        lambda x: task_str(x["dataset"], x["src_domains"], x["target_domains"]), axis=1
    )
    return df.assign(task=new_col)


def unify_validator_columns(df):
    new_col = df.apply(
        lambda x: validator_str(x["validator"], x["validator_args"]), axis=1
    )
    df = df.assign(validator=new_col)
    return df.drop(columns=["validator_args"])


def maybe_per_adapter(df, per_adapter):
    if per_adapter:
        adapters = df["adapter"].unique()
    else:
        adapters = [None]
    return adapters


def print_validators_with_nan(df, return_df=False, assert_none=False):
    for fn in [np.isnan, np.isinf]:
        curr_df = df[fn(df["score"])]
        if return_df:
            return curr_df
        curr_df = curr_df[["validator", "validator_args"]].drop_duplicates()
        if len(curr_df) > 0:
            type_str = "NaN" if fn is np.isnan else "inf"
            print(f"WARNING: the following validator/validator_args have {type_str}")
            print(curr_df)
            if assert_none:
                raise ValueError("There should be no scores with nan or inf")


def remove_nan_inf_scores(df):
    mask = np.isnan(df["score"]) | np.isinf(df["score"])
    return df[~mask]


def remove_arg(df, to_remove):
    x = json.loads(df["validator_args"])
    return dict_to_str({k: v for k, v in x.items() if k not in to_remove})


def remove_arg_from_validator_args(df, to_remove):
    new_col = df.apply(lambda y: remove_arg(y, to_remove), axis=1)
    return df.assign(validator_args=new_col)
