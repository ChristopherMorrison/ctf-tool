all: challenge.zip flag.txt

challenge.zip:
	echo 'This is a file that will be provided via CTFd to the players, generated with make' >> downloaded_file.txt &&\
	zip challenge.zip downloaded_file.txt &&\
	rm downloaded_file.txt

flag.txt:
	echo 'flag{demo}' > flag.txt

clean:
	rm challenge.zip flag.txt
