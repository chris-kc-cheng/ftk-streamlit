import calendar
import toolkit as ftk


def format_table(s):
    tbl = s.groupby([(s.index.year), (s.index.month)]).sum()
    tbl = tbl.unstack(level=1).sort_index(ascending=False)
    tbl.columns = [calendar.month_abbr[m] for m in range(1, 13)]
    tbl['YTD'] = tbl.agg(ftk.compound_return, axis=1)
    return tbl.style.format('{0:.2%}')
