"""
Output statistics from a csv file of exported Jira data
Data must contain the following fields:
- Resolution Time
- Created Time
- Issue ID
- Assignee
(C)2022 Damian Murphy
"""
import argparse
import os
import matplotlib
import numpy
import pandas
import csv

def parse_cmdline():
    """
    Parse the command line options:
        -d (debug mode on)
        <filename.csv> (required, name of file to parse for ticket info in csv format)
    :return:
    """
    # Parse any command line options.
    parser = \
        argparse.ArgumentParser(description="Generates stats from csv of jira ticket data"
                                            " provided as an arg on the command line")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="print out some extra debugging info")
    parser.add_argument("jiracsvfile",
                        help="Input file containing Jira ticket data in csv format",
                        nargs=1)
    args = parser.parse_args()
    return args

def main():
    """
    Main - Do all the work here
    :return: Nothing
    """

    global DEBUG

    cli = parse_cmdline()
    DEBUG = cli.debug

    try:
        csvdatafile = pandas.read_csv(cli.jiracsvfile[0], encoding="utf-8")
    except Exception:
        print("Cannot open " + cli.jiracsvfile[0] + "!")
        exit(1)

    # Convert columns to datetime objects
    csvdatafile[['Created', 'Resolved']] = \
        csvdatafile[['Created', 'Resolved']].apply(pandas.to_datetime)

    created_data = csvdatafile[['Created']].groupby(csvdatafile['Created']
                                                    .dt.isocalendar().week).nunique()

    closed_state = ['Closed', 'Declined', 'Awaiting Customer Verification']

    resolved_data = csvdatafile.loc[csvdatafile['Status'].isin(closed_state)]
    resolved_data = resolved_data[['Resolved']].groupby(resolved_data['Resolved']
                                            .dt.isocalendar().week).nunique()

    # print(created_data)
    # print(resolved_data)
    rate_of_closure = 0
    total_created = 0
    total_resolved = 0
    print("==================")
    print("Week\tCreated\tResolved\tVelocity")
    for index, row in resolved_data.iterrows():
        # Take care here, some weeks can have zero items, so avoid index errors
        try:
            numcreated = pandas.to_numeric(created_data['Created'][index])
        except:
            numcreated = 0
        try:
            numresolved = pandas.to_numeric(resolved_data['Resolved'][index])
        except:
            numresolved = 0

        if numcreated != 0:
            rate_of_closure = round((numresolved / numcreated), 2)
        else:
            rate_of_closure = 0

        total_created += numcreated
        total_resolved += numresolved

        print(index, numcreated, numresolved, rate_of_closure, sep='\t', end='\n')

    backlog = total_created - total_resolved
    av_created = round(total_created / len(resolved_data.index), 2)
    av_resolved = round(total_resolved / len(resolved_data.index), 2)
    av_roc = round((total_resolved / total_created), 2)
    est_weeks = 0
    
    if backlog < 0:
        est_weeks = 0
    elif av_created > av_resolved:
        est_weeks = numpy.Infinity
    elif av_created < av_resolved:
        est_weeks = round(backlog / (av_resolved - av_created), 2)

    print("-----------------------")
    print("Total Created:", total_created)
    print("Total Resolved:", total_resolved)
    print("Average Rate of Closure:", av_roc)
    print("Average Items Closed per Week:", av_resolved)
    print("Average Items Created per Week:", av_created)
    print("Weeks to close backlog of", backlog, "items is", est_weeks, "weeks")
    # fig = created_data.plot.line()
    # dia = fig.get_figure()
    # dia.savefig("created.png")
    #
    # fig = resolved_data.plot.line()
    # dia = fig.get_figure()
    # dia.savefig("resolved.png")

if __name__ == "__main__":
    main()