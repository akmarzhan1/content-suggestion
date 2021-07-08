###
FROM python:3.6

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Set the working directory to /web
WORKDIR /web
# # # Copy the current directory contents into the container at /web
# ADD . /web

RUN apt-get update \ 
&& apt-get install -y --no-install-recommends git \ 
&& apt-get -y install gcc mono-mcs \
&& apt-get purge -y --auto-remove \ 
&& rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
COPY requirements-integration.txt /web
# RUN pip install -r requirements.txt
RUN pip install -r requirements-integration.txt

COPY /web /web
CMD flask run