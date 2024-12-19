# [TEAW-Elections](https://github.com/besser435/TEAW-Elections)
This is a set of tools to run [RCV](https://en.wikipedia.org/wiki/Instant-runoff_voting) elections. 


## About
In `src/discord_bot` there is a Python script for a Discord bot. This bot handles voter registration, and votes. 
It also updates The People about the election results in real-time.


In the `outdated` directory, there is the old Google Form validation script. The original premise for this system
was to run a RCV elections through a Google Form. Now we just do a popular vote, using the Discord bot for the voting.

Registering to vote is kind of outdated now that votes are all handled in Discord, but we will keep it as we may switch
back the old system. We could also remove the storage of Discord usernames and IDs in the future to keep votes
anonymous from the Election Committee, and as such, this system would still be required.


The code is self documenting :theenotroll:
 

## Contributing
[DB Browser for SQLite](https://sqlitebrowser.org/) is a very helpful tool for visualizing the database. 

Pull requests are welcomed, but may be rejected at the Election Committee's discretion. 

