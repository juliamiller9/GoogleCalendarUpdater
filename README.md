# Google Calendar Updater
Written for the University of Washington Medical Cyclotron facility. This code automatically updates a Google calendar with patient treatments. I parse an html file that contains all upcoming treatments and organize the events in a pandas dataframe, removing all patient-identifying information. To ensure events aren't added twice, I delete all events added the last time the calendar was updated, before adding events. I save the id of each added event so they can be grabbed for deletion the next time the code runs.

See troubleshooting.txt for further info 
