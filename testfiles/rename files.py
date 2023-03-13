# Q: can you write me a code dat renames all files in a folder to a specific namin scheme?
# A: yes, but it's not a good idea to do it this way.  It's better to use the os.rename() function.
#    This is because if you have a file named "foo.txt" and you rename it to "bar.txt", then
#    you have a file named "bar.txt" and a file named "foo.txt".  If you then rename "bar.txt"
#    to "foo.txt", you have two files named "foo.txt".  This is a problem because you can't
#    have two files with the same name in the same folder.  The os.rename() function will
#    overwrite the existing file with the new file, so you don't have to worry about this.
#    Also, the os.rename() function is faster than this method.
#    This is a good example of why you should always read the documentation before you ask
#    a question.  The documentation for the os module is here:


import os

# get the current working directory
cwd = os.getcwd()+'/data/Guralp/json/'

# get a list of all the files in the current working directory
files = os.listdir(cwd)

# loop through the files
for file in files:
    # get the name of the file without the extension
    print(type(file))
    name, ext = os.path.splitext(file)
    typ, date = name.split(' - ')

    # name = name.replace('Guralp Sensor Data','fourier')
    newname = 'Guralp Sensor Data' + ' - '+ date + ext

    # rename the file
    os.rename(cwd+file, cwd+newname)
    print(newname)
    

# print a message to the user
print("All files renamed.")

