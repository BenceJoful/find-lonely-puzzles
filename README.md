# find-lonely-puzzles

"find-lonely-puzzles" is a discord server bot designed specifically for the CTC Fan Server.

## Public Commands

### lonelypuzzles

The bot exposes a single public command "lonelypuzzles" and responds to this command with a message listing the untested puzzles from one of the puzzle testing submissions channels.

Slash command syntax:

    /lonelypuzzles puzzle_type: Word Puzzles max_age: Week solved_count: 2 search_terms: crossword

Where:

* puzzle_type is one of "Sudoku", "Word Puzzles", "Other Puzzles"
* max_age is one of "Day", "Week", "Month", "Year". Defaults to Week.
* solved_count is the maximum number of people who marked it as solved. Default to 0.
* search_teams are words that are required to exist in the submission

@Mention syntax:

    @{botname} lonelypuzzles puzzle_type max_age solved_count search_terms

Where:

* puzzle_type is one of "sudoku", "word", "other" (required)
* max_age is the number of days (required)
* solved_count is the maximum number of people who marked it as solved. (required)
* search terms are optional, and not in quotes

## Private Commands

These commands are only available when the Bot is mentioned in a message sent from a specific configured bot or developer.

### echo

Post the message content as an embed.

### updatepins

Finds the pinned messages in the current channel which were posted by this bot and contain embeds, then update the embed with the current lonely puzzles. The title of the embed is parsed to create the arguments for the lonelypuzzles command.

### downloaddb

Responds with a csv file containing the list of all puzzles.

### updatedb

Updates DB stats for archive and monthly archive, based on from_date and to_date.
Requires channel (one of "Archive","Monthly_Archive"), from_date (in format "dd.Month.YYYY", e.g. "21.June.2018"), to_date.  
Dates will be inclusive: i.e. beginning of from_date to end of to_date.

### searcharchive

Searches archives for puzzles fitting the criteria.  
e.g. Top ten mindblowing tapas of all time "@PuzzleDigestBot search Archive 21.June.2000 1.December.2021 0 5 0 99999 0 3 mindblowingpuzzle desc 10 tapa title=Show Me"

Parameters:

* archive_name (one of "Archive" or "Monthly_Archive")
* from_date (in format "dd.Month.YYYY", e.g. "21.June.2018").  Dates in UTC.
* to_date, same format as above.  Inclusive, i.e. search results are from beginning of from_date to end of to_date.
* min_difficulty integer 0-5
* max_difficulty integer 0-5 (e.g. 2 would give results with ratings up to 2.99999)
* min_rating_raw integer 0+  (e.g. 2 would give results rated 2 or higher)  Raw rating gives 1 point for goodpuzzle, 2 for greatpuzzle, 3 for exceptionalpuzzle.  No upper limit.
* max_rating_raw integer 0+  (e.g. 4 would give results with ratings up to 4)
* min_rating_avg integer 0-3 (e.g. 2 would give results rated 2 or higher)  Avg rating gives 1 point for goodpuzzle, 2 for greatpuzzle, 3 for exceptionalpuzzle, then averages based on the number of votes.
* max_rating_avg integer 0-3 (e.g. 1 would give results with ratings up to 1.99999)
* order_by (one of "difficulty","rating_avg","rating_raw","reaction_count","beautifultheme","beautifullogic","inventivepuzzle","mindblowingpuzzle","age")
* sort_order (one of "asc", "desc")
* max_results integer
* search_terms (zero or more words that must exist in first line of puzzle submission - can include tags, author, etc.)
* title (zero or more words that will appear as the title of the embedded results.  This parameter alone must be preceded by its name: e.g. "title=Show Me")

## Events

This bot listens for the following events

### on_message

Listens for messages posted to the archive and checks that the puzzle number in the message is one more than the previous message. Sends a message to the author and the moderator.

Messages which mention this bot are processed like a command

