# Reflection 06b — Polyglot Persistence & the Decision

## What is my take-away from this module?

In this module, I learned more about different types of databases and when we should use each one.

I also understood the difference between SQLite and PostgreSQL and how we can store different types of data using JSON and key-value storage.

Before this module, I mainly focused on relational databases, but now I understand that there are different ways to store and manage data.

The most important thing I understood is that before choosing a database, we need to know the requirements of our project. A database that works well for one application might not be the best choice for another application.

## What went well?

Understanding the difference between a local database and a server-based database was easy for me.

Also, working with SQLite was easier because we already used it in almost all the previous modules.

The knowledge from Module 04 about transactions and data integrity helped me understand why reliable transactions are important.

I also liked the database decision task because it gave me the opportunity to think about which database I would choose in different situations instead of only writing SQL queries.

## What was difficult?

At the beginning, it was difficult for me to understand the difference between ACID, BASE and CAP and when each concept is important.

I also found it a little difficult to understand how two JSON queries can give the same result but have different execution plans.

Another difficult part was understanding how databases handle multiple users who want to write data at the same time.

I think I need more practice with PostgreSQL because most of my experience until now has been with SQLite.

## What did I explore?

I explored how JSON works in SQLite and how we can add new information without changing the whole database structure.

I also looked at the differences between Python Shelve and SQLite and how PostgreSQL allows multiple users to access the same database.

One thing I found interesting is that SQLite can be used for more than just relational tables. It can also work with JSON and key-value storage.

In mechatronics and automation, different machines can have different specifications and sensor information. Using JSON could make it easier to store this information without changing the database structure every time we add a new machine.

## How were the interactions with my Task Pod?

I used my group members' work as a reference to understand the tasks better.

Looking at different approaches helped me understand how to choose a suitable database for different situations.

I think discussing our decisions together is useful because each person might have a different opinion about which database is better and why.

This also helps us improve our communication and teamwork skills, which are important when working on engineering projects.

## Did I receive help or do any extra work?

I used the professor's instructions, my group members' work and ChatGPT to understand some of the new concepts.

I also reviewed the differences between SQLite, DuckDB and PostgreSQL to understand how the topics from Module 06a and Module 06b are connected.

This knowledge will also help me when choosing a database for my final project in Module 07.

I still need to run the benchmarks on my own laptop and verify the PostgreSQL concurrency behaviour.

## What could I improve next time?

Next time, I would like to spend more time practising with PostgreSQL and understanding how server-based databases work.

I also want to improve my ability to make decisions based on experimental results rather than only depending on theoretical information.

## What would I recommend to someone doing this module?

I would recommend understanding the advantages and disadvantages of each database before starting the tasks.

It is important not to choose a database only because it is faster. We should also consider the type of data, the number of users, reliability and the requirements of the project.

My advice is to try to connect the knowledge from all the previous modules because this module brings many of the concepts we studied together.

I think this will also make it easier to start the final project and explain why we chose a specific database.

