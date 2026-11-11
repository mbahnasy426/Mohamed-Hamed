# Reflection 05 — Normalization vs. Denormalization

## Take-away: what do I want to remember?

In this module, I learned more about normalization and denormalization and why they are important when working with databases.

I learned that normalization helps us organize the data into different tables to avoid repeating the same information. On the other hand, denormalization combines data to make some queries faster, especially when we want to create reports.

Another important thing I learned is that we need to find a balance between keeping our data organized and improving the performance of the database.

## What worked well?

The good thing about this module was that I started to understand the difference between normalization and denormalization by comparing the examples.

I worked with a database containing 200,000 rows and separated the data into different tables, such as machine, part, job and job_part.

I also found it interesting that we could get the same results using normalized and denormalized tables, even though the way the data was stored was different.

## What was difficult or surprising?

At the beginning, understanding normalization and denormalization was a little confusing for me, especially when deciding which one is better to use.

Something that surprised me was that denormalization does not always make queries much faster. I also learned that indexes can sometimes make queries slower instead of faster.

I needed to go through the examples more than once to understand why this happens.

## Exploration and performance

In this module, I explored how normalization and denormalization affect the performance of a database.

I compared queries using different tables and checked how long they take to execute. I also learned about update, insert and delete anomalies and why normalization helps us avoid these problems.

Another thing I explored was how indexes affect query performance and how the database uses storage.

The performance results came from an independent test environment, so I still need to run the tests on my own laptop to compare the results.

## Interaction with peers and instructors

Unfortunately, I was not able to attend the Module 5 session, so I missed the discussions with the other groups and the instructor.

I tried to understand the module by going through the tasks and examples independently. I still need to discuss some of the questions with my classmates to understand their approaches and learn from their results.

## Help, tools and extra work

I used ChatGPT to help me understand some concepts, especially the difference between normalization and denormalization and how they affect database performance.

I also used the SQL scripts and test results to understand how the database works. The tests helped check that the data was correct and that both methods gave the same results.

I think I still need more practice with normalization, especially deciding how to separate data into tables correctly.

## My conclusion

My main takeaway from this module is that normalization is important for keeping the data organized and avoiding problems, while denormalization can be useful when we want to improve reporting performance.

I also learned that making a database faster is not always about using more indexes or combining tables. We need to understand the structure of the database and test different solutions.

Even though I missed the session, I think this module helped me understand more about database design, and I will try to practice these concepts more.
