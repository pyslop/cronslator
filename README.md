# cronslator

## Natural Language to Cron

A Python 3.9+ library to convert an English string to cron schedule.

## Important

> This is not the library you are looking for!

This codebase was generated entirely from prompting
GitHub Copilot (Clause 3.5 Sonnet) and has not been
audited, verified or even assumed to be correct.

This is an experiment to tinker with new shiny tools,
and to share what's possible using them -
your takeaway could be "Wow, that's nice!" or "Wow, that's crap!"
and either are fine.

Beyond this line, there is no human written text or code,
it is all LLM generated slop (hence the org name pyslop!).

## Understanding Cron Format

The cron expressions generated follow the standard 5-field format:

```ascii
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * *
```

Special characters:

- `*`: any value
- `,`: value list separator
- `-`: range of values
- `/`: step values
- `L`: last day of month (only in day of month field)

Examples:

| Natural Language Description | Cron Expression |
|----------------------------|-----------------|
| Every Monday at 3am | `0 3 * * 1` |
| Every weekday at noon | `0 12 * * 1-5` |
| Every 15 minutes | `*/15 * * * *` |
| First day of every month at midnight | `0 0 1 * *` |
| Every Sunday at 4:30 PM | `30 16 * * 0` |
| Every hour on the half hour | `30 * * * *` |
| Every day at 2am and 2pm | `0 2,14 * * *` |
| Every 30 minutes between 9am and 5pm on weekdays | `*/30 9-17 * * 1-5` |
| First Monday of every month at 3am | `0 3 1-7 * 1` |
| Every quarter hour between 2pm and 6pm | `*/15 14-18 * * *` |
| Every weekend at 10pm | `0 22 * * 0,6` |
| Every 5 minutes during business hours | `*/5 9-17 * * 1-5` |
| 3rd day of every month at 1:30am | `30 1 3 * *` |
| Every weekday at 9am, 1pm and 5pm | `0 9,13,17 * * 1-5` |
| At midnight on Mondays and Fridays | `0 0 * * 1,5` |
| Twice daily at 6:30 and 18:30 | `30 6,18 * * *` |
| Monthly on the 15th at noon | `0 12 15 * *` |
| Three times per hour at 15, 30, and 45 minutes | `15,30,45 * * * *` |
| Last day of month at 11:59 PM | `59 23 L * *` |
| Weekdays at quarter past each hour | `15 * * * 1-5` |
| Once per hour in the first 15 minutes | `0-14 * * * *` |
| Workdays at 8:45 AM except on the 13th | `45 8 1-12,14-31 * 1-5` |
| First 5 days of each quarter at dawn | `0 6 1-5 1,4,7,10 *` |
