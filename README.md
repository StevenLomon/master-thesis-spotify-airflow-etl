# Master Thesis: Spotify ETL using Airflow and Snowflake

This is a README that is created in retrospect. (It will mostly be my actual master thesis translated from Swedish to English haha). As much as possible will be kept as close to the initial state that was left in before the deadline of the master thesis. To honor this, this is the other reposity that was also used during the coding of the project:  
https://github.com/StevenLomon/master-thesis-spotify-ec2  

The Google Colab notebook that was used during the project:  
https://colab.research.google.com/drive/1VNzOMly5cGOHLtu8g8HUzPFyuyhaikQ5  

The actual master thesis is available to read (altho in Swedish haha) [here](/master-thesis.pdf)

## Description
My master thesis project! It was worked on for just under a month were 20 days were put aside for the actual implementation of the project and the rest for writing the thesis and presenting it.  

## Technologies used and project architecture
* Amazon EC2
* PostgreSQL
* Apache Airflow
* Amazon S3
* Snowflake

The project follows the following architecture: (this one is updated from the one in the master thesis. Snowflake is not part of AWS haha)
!["Project architecture diagram"](/project-architecture-diagram.png "Project architecture diagram")

Google Colab has been used over Jupyter Notebook purely out of personal preference.  

My reasoning for switching from Amazon Redshift to Snowflake mid-project was the following: for this overall educational purpose, it was reasoned that it's easier and more intuitive to learn Snowflake. Redshift feels more niche and necessary to learn if one is to work at a company that uses Redshift and if so, training will be provided from the company for the specific areas and specifications at the company. Snowflake has extensive documentation and felt more beginner friendly. It also feels easier to learn Redshift is one has experience of working with another data warehouse, i.e. Snowflake, in the toolbelt.

## Project journal  

###

### Loading the data into Snowflake
!["The first 15 rows of data in the Snowflake table fact_tracks sorted by popularity with metadata to the right"](/master-thesis-images/snowflake-table.png "The first 15 rows of data in the Snowflake table fact_tracks sorted by popularity with metadata to the right")
The first 15 rows of data in the Snowflake table fact_tracks sorted by popularity with metadata to the right.  

## End-of-project Reflections and Improvements
The final result differs quite a bit from the initial project description and vision. This is partly because it's hard to completely predict how a project will go from square zero which makes it important to execute the project with iteration in mind. The result now at the finish line is that I was more complex data in Postgre. All of this is complete separate from the Airflow pipeline that has been created. This one takes simpler data from the API, transforms it and loads it in a data warehouse in Snowflake. A star schema has been created for both the data in PostgreSQL and in Snowflake to store the data in fact tables and dimension tables.  

The shortcomings are both technical, as in the case of Spotify's rate limit and that I wasn't able to have Airflow co-operate with parquet files, and also theoretical. The changes in my dimension model arise completely from the fact that I don't have a stable foundation and deep understanding for star schemas and that type of modeling with fact tables and dimension tables yet. A lot of understanding have been picked up along the way to be nurtured and re-inforced via self studies on the side. There's been a lot of bumps in the road but using AI as a tool when coding makes everything very manageable with some determination and persistence!  

I could however have been more strategic with my time. Taking the decision of focusing on simpler data in the Airflow ETL earlier would have lessen the stress around the project significantly. Despite the DAG that I designed in Airflow differing a lot from what I had in the beginning of the project, I am still very pleased with the fact that I've handled all of these new technologies with genuine curiosity and a willingness to learn and also that I've actually designed a fully automated end-to-end ETL pipeline from API to data warehouse. It's been fruitfil seeing these principles that I've reading about Data Engineering put into practice.  

Wisdom for the future: Planning, planning, planning. But this gets easier and easier with iteration and experience you pick up with every project taken from start to finish! Overall this project has been super fun and super educational!  

There are improvements that I haven't been able to handle. A fully automated pipelines that actually extracts data from the 50 biggest playlist with the more advanced transformations applied, finding a way around the API rate limit, is certainly one of the biggest improvements that can be made. Part of the feedback that I got when I presented the project is that AWS Glue could be used to simplify things considerably. Otherwise it's an end-to-end pipeline that can be scaled without too much hassle and where the individual parts can switch as needed.  

When it comes to the data that is now stored in both Postgre and Snowflake; it can be used for data visualization and data analysis och when grown big enough it could be used for Machine Learning models. To take things one step further, the data could automatically be visualized in a dashboard or similar. This is something that could be done together with a Data Scientist and one of the many cool things I'm more than willing to do as a Data Engineer!
