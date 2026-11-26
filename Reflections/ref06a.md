# Reflection 06a — The Analytical Engine (DuckDB)

## What is my take-away from this module?

In this module, I learned more about DuckDB and the difference between analytical and operational databases. Before this module, most of my knowledge was about SQLite, but now I understand why we sometimes need a different database for analysing large amounts of data.

I understood that SQLite is better for small and frequent transactions, while DuckDB is more suitable for analysing historical data and creating reports.

I also learned that we do not always need to replace one database with another. We can use both databases in the same project, where each one has its own purpose.

## What went well?

Understanding the difference between SQLite and DuckDB was not that difficult because we already worked with SQLite in the previous modules.

The knowledge from Module 03 about execution plans and Module 05 about normalization and denormalization helped me understand this module better.

I also liked that this module was connected to the previous modules because it helped me understand how everything we studied can be used together.

## What was difficult?

At the beginning, it was difficult for me to understand how Parquet works and why storing data in columns can improve performance.

Also, understanding the execution plans in DuckDB was a little difficult because they are different from SQLite.

Another thing that needed more attention was understanding how to compare the performance of two databases correctly. It is not enough to run a query one time and decide which database is faster.

## What did I explore?

I explored how we can convert data from SQLite to Parquet and how DuckDB can be used to analyse large amounts of historical data.

I also looked at the difference between Snappy and Zstd compression and how we can reduce the file size without losing information.

As a mechatronics and automation student, I found this interesting because machines and sensors can produce a large amount of data. We could use SQLite to collect the data and DuckDB to analyse the machine performance over a longer period.

## How were the interactions with my Task Pod?

I used the material from my group members as a reference to help me understand the tasks and organise my work.

Looking at different solutions is helpful because sometimes another person understands a concept in a different way, which makes it easier for me to understand.

I think working together and discussing the results is important, especially when we are learning about a new technology.

## Did I receive help or do any extra work?

I used the professor's instructions, my group members' work and ChatGPT to understand some concepts that were difficult for me.

I also reviewed some topics from the previous modules to understand the connection between query performance, indexes and analytical databases.

I still need to verify the benchmark results on my own laptop.

## What could I improve next time?

Next time, I would like to spend more time understanding the concepts before starting the practical tasks.

I also want to improve my ability to read execution plans and explain why a query is faster instead of only looking at the execution time.

## What would I recommend to someone doing this module?

I would recommend understanding the difference between operational and analytical databases first before starting the tasks.

It is also important to make sure that both databases give the same results before comparing their performance.

My advice is not only to focus on finishing the tasks but also to understand why we are doing each step and how we can use this knowledge in a real project.
