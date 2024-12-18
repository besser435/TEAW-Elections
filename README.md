# [TEAW-Elections](https://github.com/besser435/TEAW-Elections)
This is a set of tools to run [RCV](https://en.wikipedia.org/wiki/Instant-runoff_voting) elections. 


## About
In `src/ballot_updater` there is a Python script to take responses from a Google Form and add them to the
election database. It runs every minute, so that elections can update in real time using the Discord bot.


In `src/discord_bot` there is a Python code for a Discord bot. This bot handles voter registration, and 
will update The People about the election in near real-time.

The code is self documenting :theenotroll:
 

## Contributing
[DB Browser for SQLite](https://sqlitebrowser.org/) is a very helpful tool for visualizing the database. 

Pull requests are welcomed, but may be rejected at the election committee's discretion. 


## TODO
- Add proper docs, including how to set up the Google Form
- Discord bot vote notifications and current result command
- Add RCV algorithm
