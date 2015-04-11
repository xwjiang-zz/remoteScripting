import ssh
ptySSH = ssh.SSH("127.0.0.1", "xxx", "yyy", 22) # create SSH object and reuse it for different commands
print ptySSH.push('./t.sh', '~') # copy the test shell script to server
print ptySSH.cmd('rm -r ~/output') 
print ptySSH.cmd('mkdir ~/output') # generate an output folder that's gonna collect all the outputs
print ptySSH.cmd('~/t.sh') # run the test shell script
print ptySSH.cmd('rm ~/t.sh') 
print ptySSH.pull_dir('~/output', '.') # copy the output folder back to local
print ptySSH.cmd('rm -rf ~/output') # remove the generated output on server is optional
