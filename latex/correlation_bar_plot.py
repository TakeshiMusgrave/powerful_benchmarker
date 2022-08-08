import os

import seaborn as sns

from latex.correlation import base_filename, get_postprocess_df, get_preprocess_df
from latex.table_creator import table_creator


def reshape_and_plot(df, output_folder, basename, name):
    df = df.reset_index()
    new_col = df.apply(lambda x: f'{x["level_0"]}: {x["level_1"]}', axis=1)
    df = df.assign(validator_as_str=new_col).drop(columns=["level_0", "level_1"])
    df["validator_as_str"] = df["validator_as_str"].str.replace(
        "\\tau", "τ", regex=False
    )
    dfm = df.drop(columns=["Mean", "Std"]).melt(id_vars=["validator_as_str"])
    assert "Mean" not in dfm["variable"].values
    assert "Std" not in dfm["variable"].values
    order = df.sort_values("Mean", ascending=False)["validator_as_str"].values
    xlabel = (
        "Weighted Spearman Correlation"
        if name == "weighted_spearman"
        else "Spearman Correlation"
    )

    sns.set(style="whitegrid", rc={"figure.figsize": (12, 12)})
    plt = sns.barplot(
        x="value",
        y="validator_as_str",
        data=dfm,
        ci="sd",
        order=order,
        color="lightskyblue",
        errwidth=1.5,
        capsize=0.1,
    )
    plt.set(xlabel=xlabel, ylabel="Validator", xlim=(-100, 100))
    fig = plt.get_figure()
    fig.savefig(
        os.path.join(output_folder, f"{basename}_barplot.png"), bbox_inches="tight"
    )
    fig.clf()


def correlation_bar_plot(args, per_adapter, name, src_threshold):
    basename = base_filename(name, per_adapter, src_threshold)

    df, output_folder = table_creator(
        args,
        basename,
        preprocess_df=get_preprocess_df(per_adapter),
        postprocess_df=get_postprocess_df(per_adapter),
        do_save_to_latex=False,
    )

    reshape_and_plot(df, output_folder, basename, name)