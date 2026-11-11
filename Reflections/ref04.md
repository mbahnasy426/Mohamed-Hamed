# Reflection 04 — Data Integrity, Constraints & Edge Triggers

## Take-away: what do I want to remember?

In this module, I learned more about data integrity and how to make sure that the data in the database is correct. I learned that there are three types of integrity: entity, referential and domain integrity. I also learned how to use PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE and CHECK.

Another important thing I learned is that we should not depend only on Python to check the data because the database itself should also have rules to prevent wrong data. I also learned about UPSERT and how it helps us avoid duplicate data.

## What worked well?

The good thing about this module was that the tests helped me understand how the constraints work. When we try to insert wrong data, such as an invalid temperature or a sensor that does not exist, the database rejects it.

I also found the triggers interesting because they can automatically create an alarm when the vibration is too high. Another good thing was that inserting the same CSV file twice did not create duplicate readings.

## What was difficult or surprising?

At the beginning, I found it a little difficult to understand the difference between constraints and triggers and when we should use each one.

Something that surprised me was that CHECK does not reject NULL values by itself, so we also need NOT NULL. I also learned that STRICT does not reject every text value because SQLite can convert some numeric text into numbers.

I needed to go through the examples more than once to understand these things better.

## Exploration and performance

In this module, I explored how triggers can affect the performance of the database. The test compared inserting 10,000 readings with and without a trigger, and the results showed that triggers can make inserting data slower because the database has extra work to do.

I also learned about INSTEAD OF INSERT triggers and how they can be used with views.

The performance results were tested in another environment, so I still need to run them on my own laptop to compare the results.

## Interaction with peers and instructors

For this module, I used the same database structure and sample CSV as Nassar to keep our work consistent. I think working with the same structure is important because it makes it easier to compare our results and understand the tasks.

I still need to complete the discussion with the other pod and get feedback about our work.

## Help, tools and extra work

I used ChatGPT to help me understand some concepts and prepare the code, especially constraints, triggers and UPSERT. I also used VS Code and the test results to check how the database behaves.

The tests were run in another environment, so I still need to run the code on my laptop and make sure everything works correctly.

I think I need more practice writing triggers by myself because this was one of the new things for me in this module.

## Status

Task A, Tasks 1–4 and the optional Task 5 were implemented and tested in another environment. I still need to verify the results on my own PC and complete the pod discussion.

## Conclusion

My main takeaway from this module is that a database should not only store data but also make sure that the data is correct. I learned how constraints and triggers help us prevent mistakes and how UPSERT can avoid duplicate data. I think I understand these concepts better now, but I still need more practice to be able to use them without help.
