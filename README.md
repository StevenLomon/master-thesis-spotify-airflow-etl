# Master Thesis: Spotify ETL using Airflow and Snowflake

This is a README that has been created in retrospect. (It will mostly be my actual master thesis translated from Swedish to English haha. I wish I had documented the specific challenges I faced in regards to EC2, Airflow, Snowflake but also overall throughout the entire project and how I overcame them more as I was overcoming them. It's 3 months ago now I did this and I can't really recall. Document!! It helps everyone included. This is a reminder to myself, my future and self and anyone reading this haha! More on this down [here](#notes-on-bad-documentation))

As much as possible it will be kept as close to the initial state that was left in before the deadline of the master thesis. To honor this, this is the other reposity that was also used during the project when coding for the virtual machine environment:  
https://github.com/StevenLomon/master-thesis-spotify-ec2  

The Google Colab notebook that was used during the project:  
https://colab.research.google.com/drive/1VNzOMly5cGOHLtu8g8HUzPFyuyhaikQ5  

The actual master thesis is available to read (altho in Swedish haha) [here](/master-thesis.pdf)

## Description
My master thesis project for my studies at Teknikhögskolan as Python Developer with Specialization in AI! A full ETL pipeline that takes data end-to-end from the Spotify API to a Snowflake Data Warehouse. It was worked on for just under a month where 20 days were put aside for the actual implementation of the project and the rest for writing the thesis and presenting it. 

## Technologies used and project architecture
* Amazon EC2
* PostgreSQL
* Apache Airflow
* Amazon S3
* Snowflake

The project uses the following architecture: (this one is updated from the one in the master thesis. Snowflake is not part of AWS haha)
!["Project architecture diagram"](/project-architecture-diagram.png "Project architecture diagram")

Google Colab has been used over Jupyter Notebook purely out of personal preference.  

My reasoning for switching from Amazon Redshift to Snowflake mid-project was the following: for this overall educational purpose, it was reasoned that it's easier and more intuitive to learn Snowflake. Redshift feels more niche and necessary to learn if one is to work at a company that uses Redshift and if so, training will be provided from the company for the specific areas and specifications at the company. Snowflake has extensive documentation and felt more beginner friendly. It also feels easier to learn Redshift is one has experience of working with another data warehouse, i.e. Snowflake, in the toolbelt.

## Project journal  

### Data modeling
All data modeling was done in Lucidchart. Both the standard one and the dimension model one went through several iterations throughtout the duration of the project. In the beginning the thought was that three tables were to be used: Track, Artist and Playlist. A central question in the beginning was "Am I modeling Spotify or my database?" The answer is "my database" and with the solidified, the cardinalities became rather obvious.

!["The very first iteration of the data modeling for the Spotify data. The two tables to the left ended up not being used at all"](/master-thesis-images/first-data-modeling-iteration.png "First data modeling iteration")
The very first iteration of the data modeling for the Spotify data. The two tables to the left ended up not being used at all.  

The iteration led to the creation of two distinct datasets; one more complex and a simpler one. How the data modeling for the complex dataset was translated in PostgreSQL below:
!["The final ERD for the database in PostgreSQL"](/master-thesis-images/ERD.png "Final PostgreSQL ERD")
The final ERD for the database in PostgreSQL.  

When it was time to model a dimension model after the complex dataset it was decided that there are too few dimension tables which once again affected how the data was extracted and transformed.  

!["Dimension model for the final complex data in PostgreSQL"](/master-thesis-images/dimension-model.png "Dimension model")
Dimension model for the final complex data in PostgreSQL.  

### Data extraction
All data is extracted from the Spotify API. Initially this included creating an app in their dashboard and going through an authentication process.  

In the beginning of the project the thought was clear to extract all songs from the 50 biggest playlists and creating a dataset of ca 5000 songs. Further columns with data would also be extracted from Spotify's audio features API endpoint. This idea was iterated upon throughout the project. In the beginning, only 'energy level' and 'danceability' was extracted but eventually the data was loaded into PostgreSQL used all data available from audio feautres to give more data to the dimension table that later was created.  

The very biggest problem that arised at this stage of the project was audio feautures itself and its rate limit which was more prominent than other endpoints. This was worked around by amongs other things save intermediate data in JSON-files to built the dataset iteratively and continue building the pandas DataFrame from a specific point. However, this was only executable in Google Colab and not in Airflow since they are run in two different environments. With this the need for the simpler dataset that eventually was used in Airflow was born.  

So except for a complex dataset with songs from the 50 biggest playlists in Sweden was created and also a simpler dataset where only the 50 songs from Spotify's Global Top 50 was extracted. The second big problem that arised during the project which led to the need of a simpler dataset occured during data transformation:

### Data transformation in Google Colab
All data transformation was written in Google Colab initally and executed with the help of the Python library pandas. With two distinct datasets came two distinct chains of data transformations. Early on in the project it was decided to make use of the fact that PostgreSQL can manage lists as a datatype by having two columns be of type list: 'playlist sources' and 'genres'. Thus, these are lists of strings.  

A problem here however is that when a DataFrame is saved as csv, all data is converted to text meaning that all lists lose their properties and functionality. The solution to this was to use the Parquet file format. By using this file format, complex datatypes like lists keep their properties when being exported out of a Notebook.  

The other big problem that arised during the project is that Parquet files turned out to not be compatible with Airflow. This became the second reason that a simpler dataset had to be built to be used with Airflow. Since a lot of time and energy had been spent on the more complex dataset, it wasn't thrown away and instead of got to lie stored in PostgreSQL completely separate from Airflow.  

!["Advanced data transformations with pandas to aggregate data in the complex dataset. df_aggregated was later saved as a Parquet file"](/master-thesis-images/complex-data-transformation.png "Complex data transformation")  
Advanced data transformations with pandas to aggregate data in the complex dataset. df_aggregated was later saved as a Parquet file.  

!["Function in spotify_etl.py that is used in spotify_dag.py to transform the simpler dataset"](/master-thesis-images/simple-data-transformation.png "Simple data transformation")
Function in spotify_etl.py that is used in spotify_dag.py to transform the simpler dataset.

The simple data that has Snowflake as its final destination is loaded into a S3 bucket after being transformed.  

### Loading the complex data into PostgreSQL
After the data transformation stage, the complex data that is to be loaded into PostgreSQL is stored in a Parquet file. This Parquet file is read into a DataFrame in a Python script and loaded into Postgre by using the library psycopg2:
!["The last rows in db.py that loads the data into PostgreSQL using Python and psycopg2"](/master-thesis-images/loading-data-into-postgresql.png "Loading data into PostgreSQL")  
The last rows in db.py that loads the data into PostgreSQL using Python and psycopg2.  

### Setting up the EC2 instance and DAG in Airflow
At this point the DAG had been set up and an Airflow instance had been initiated using Amazon EC2. (I'm noticing now that I don't really write about this at all in the master thesis haha.. So the following is written now in retrospect.")

This included creating an EC2 instance in the AWS Management Console with a key pair assigned (important), waiting for it to be in a running state, and grabbing its Public IPv4 address. This IP address will be used to set a remote connection to the EC2 instance in VSCode to enable coding in the virtual machine environment with the VSCode UI. This is not mandatory since coding can be executed completely within the terminal using a text editor like Vim (my favorite haha) or Nano but going with the Remote-SSH option and coding for the EC2 instance in VSCode is more beginner friendly

To set up the remote SSH connection, the blue button in the very lower left corner in VSCode is pressed followed by "Connect to Host...". After clicking "Configure SSH Hosts..." and the corresponding config file to the current user, the config file is edited. The public IPv4 address and the location of the key pair file is added in the following format:
```
# Read more about SSH config files: https://linux.die.net/man/5/ssh_config
Host spotify-airflow-master-thesis
    HostName 16.170.110.224
    User ubuntu
    IdentityFile C:\Users\steve\Documents\airflow_ec2_key.pem
```

When coding in the virtual machine environment, the second GitHub repo was set up. Once again, it can be found here:  
https://github.com/StevenLomon/master-thesis-spotify-ec2  

The DAG code was written in Python following the convention found in the official Apache Airflow documentation:  
https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html  
The DAG was initiated mostly with the default arguments and three tasks were created. These were executed in a simple 1, 2, 3 order.

The extracted raw data that later became the simple dataset was loaded into another separate S3 bucket using the BashOperator in the DAG:
!["The final lines of code in spotify_dag.py where we define our DAG and the raw data is loaded onto an S3 bucket. The transformed data is loaded into an S3 bucket in the function transform_data a few lines above"](/master-thesis-images/spotify_etl_dag.png "The full DAG")  
The final lines of code in spotify_dag.py where we define our DAG and the raw data is loaded onto an S3 bucket. The transformed data is loaded into an S3 bucket in the function transform_data a few lines above.  

!["The full DAG that was created viewed in Airflow"](/master-thesis-images/full-dag.png "The full DAG viewed in Airflow")  
The full DAG that was created viewed in Airflow.  

#### Notes on bad documentation
(Once again; I wish I had documented the specific challenges I faced in regards to EC2, Airflow and Snowflake as I faced them! The only thing I wrote in my project journal on the 24th of May was "Today I made big progress on Airflow. Wrote all code for the Spotify DAG". That's absollutely terrible and helps no one!! 😅 I can't look back at that and re-visit my state of mind as I was coding that day. What challenges did I face and how did I overcome them? What neat little tricks did I learn? What went better than expected? How did I fail forward? On the 25th I wrote: "Today I fixed this warning in the Airflow console: 'The scheduler does not appear to be running. Last heartbeat was received May 23, 2024 12:02 PM. The DAGs list may not update, and new tasks will not be scheduled.'". But that was it! Not *how* I actually fixed it and what to think about in the future! What??? Let's forgive ourselves for not knowing any better at the time but take full responsibility now that we do haha)

### Setting up the Snowpipe trigger for transfer from S3 to Snowflake
(The only thing I wrote in my project journal regarding Snowpipe and Snowflake was the following: "Fixade en hel del buggar för att få hela vår DAG att funka och började sedan skriva SQL för att sätta upp vår Data Warehouse i Snowflake. Att skriva all kod för att sätta upp vår Snowpipe och ladda data automatiskt från vår S3 bucket till vår databas i vår data warehouse i Snowflake var relativt enkelt. Enda grejen är att den inte kommer ta hänsyn till dubletter alls vilket krävde mer komplicerad kod för att merge data när vi är in the Snowpipe stage". -> "Fixed a couple of bugs to get the full DAG to work (present me is wondering "How did you fix those bugs? I'm CURIOUS) followed by starting to write SQL to set up our Data Warehouse in Snowflake. Writing all the code to set up Snowpipe and load data automatically from our S3 bucket to our database in our data warehouse in Snowflake was relatively easy. (Were there any obstacles?) The only thing is that it won't take duplicates into consideration at all which required more complicated code to merge data when we are in the Snowpipe stage." The only thing I remember now in retrospect is that the process included grabbing the ARN of the S3 bucket. That's it. I wanna know my trains of thought as I was writing this complicated code)  

When the transformed data is put in its S3 bucket, a trigger set up using Snowpipe automatically copies the data from the csv file into a table in Snowflake. This data transfer is not part of Airflow.

!["The final lines of code in the SQL worksheet that was used to create and load data in a data warehouse. By default, data is loaded even if it leads to duplicated which merge_global50_tracks_task prevents"](/master-thesis-images/snowflake-sql-worksheet.png "The SQL worksheet")  
The final lines of code in the SQL worksheet that was used to create and load data in a data warehouse. By default, data is loaded even if it leads to duplicated which merge_global50_tracks_task prevents.  

The data that is loaded into Snowflake is actually simple enough that a database could do the job, but since it's not data that has a transactional purpose and instead will be stored for a longer period it was decided to create a simple dimension table and store the data in the star schema format with fact tables and dimension tables again. This was also to follow the standard of how to store data in a data warehouse.  

!["The first 15 rows of data in the Snowflake table fact_tracks sorted by popularity with metadata to the right"](/master-thesis-images/snowflake-table.png "The first 15 rows of data in the Snowflake table")
The first 15 rows of data in the Snowflake table fact_tracks sorted by popularity with metadata to the right.  

## End-of-project Reflections and Improvements
The final result differs quite a bit from the initial project description and vision. This is partly because it's hard to completely predict how a project will go from square zero which makes it important to execute the project with iteration in mind. The result now at the finish line is that I was more complex data in Postgre. All of this is complete separate from the Airflow pipeline that has been created. This one takes simpler data from the API, transforms it and loads it in a data warehouse in Snowflake. A star schema has been created for both the data in PostgreSQL and in Snowflake to store the data in fact tables and dimension tables.  

The shortcomings are both technical, as in the case of Spotify's rate limit and that I wasn't able to have Airflow co-operate with parquet files, and also theoretical. The changes in my dimension model arise completely from the fact that I don't have a stable foundation and deep understanding for star schemas and that type of modeling with fact tables and dimension tables yet. A lot of understanding have been picked up along the way to be nurtured and re-inforced via self studies on the side. There's been a lot of bumps in the road but using AI as a tool when coding makes everything very manageable with some determination and persistence!  

I could however have been more strategic with my time. Taking the decision of focusing on simpler data in the Airflow ETL earlier would have lessen the stress around the project significantly. Despite the DAG that I designed in Airflow differing a lot from what I had in the beginning of the project, I am still very pleased with the fact that I've handled all of these new technologies with genuine curiosity and a willingness to learn and also that I've actually designed a fully automated end-to-end ETL pipeline from API to data warehouse. It's been fruitfil seeing these principles that I've reading about Data Engineering put into practice.  

Wisdom for the future: Planning, planning, planning. But this gets easier and easier with iteration and experience you pick up with every project taken from start to finish! Overall this project has been super fun and super educational!  

There are improvements that I haven't been able to handle. A fully automated pipelines that actually extracts data from the 50 biggest playlist with the more advanced transformations applied, finding a way around the API rate limit, is certainly one of the biggest improvements that can be made. Part of the feedback that I got when I presented the project is that AWS Glue could be used to simplify things considerably. Otherwise it's an end-to-end pipeline that can be scaled without too much hassle and where the individual parts can switch as needed.  

When it comes to the data that is now stored in both Postgre and Snowflake; it can be used for data visualization and data analysis och when grown big enough it could be used for Machine Learning models. To take things one step further, the data could automatically be visualized in a dashboard or similar. This is something that could be done together with a Data Scientist and one of the many cool things I'm more than willing to do as a Data Engineer! :)

(As for my reflections now as Steven writing a README 3 months after the thesis has been handed in I've gotten my graduation; to past Steven, present Steven and future Data Engineer and AWS Solutions Architect Steven: document more haha)
