#
# Remote ssh cmds
#

import pty, re, os, sys, stat, getpass

class SSH: 
    def __init__(self, ip, password, user, port): # create a SSH object and reuse it 
        self.ip = ip
        self.password = password
        self.user = user
        self.port = port

    def run_cmd(self, c): # fork a psudo terminal and run ssh
        (pid, f) = pty.fork()
        if pid == 0:
            os.execlp('ssh', 'ssh', '-p %d' % self.port,
                      self.user + '@' + self.ip, c)
        else:
            return (pid, f)     
    
    def push_file(self, src, dst): 
        (pid, f) = pty.fork()
        if pid == 0:
            os.execlp('scp', 'scp', '-P %d' % self.port,
                      src, self.user + '@' + self.ip + ':' + dst)
        else:
            return (pid, f) 
    
    def pull_file(self, src, dst): 
        (pid, f) = pty.fork()
        if pid == 0:
            os.execlp('scp', 'scp', '-P %d' % self.port,
                      self.user + '@' + self.ip + ':' + src, dst)
        else:
            return self.ssh_results(pid, f)

    def push_dir(self, src, dst): 
        (pid, f) = pty.fork()
        if pid == 0:
            os.execlp('scp', 'scp', '-P %d' % self.port, '-r', src,
                      self.user + '@' + self.ip + ':' + dst)
        else:
            return (pid, f)
    
    def pull_dir(self, src, dst):
        (pid, f) = pty.fork()
        if pid == 0:
            os.execlp('scp', 'scp', '-P %d' % self.port, '-r',
                      self.user + '@' + self.ip + ':' + src, dst)
        else:
            return self.ssh_results(pid, f)

    def _read(self, f):
        x = ''
        try:
            x = os.read(f, 1024)
        except Exception: 
            pass
        return x

    def ssh_results(self, pid, f):
        output = ''
        expect = self._read(f)         # check for authenticity of host request
        m = re.search('authenticity of host', expect)
        if m:
            os.write(f, 'yes\n') 
            # Read until we get ack
            while True:
                expect = self._read(f)
                m = re.search('Permanently added', expect)
                if m:
                    break

            expect = self._read(f)         # check for password request
        m = re.search('assword:', expect)
        if m:
            # send password
            os.write(f, self.password + '\n')
            # read two lines
            tmp = self._read(f)
            m = re.search('Permission denied', tmp)
            if m:
                raise Exception('Invalid password')
            # password was accepted
            expect = tmp
        while expect and len(expect) > 0:
            output += expect
            expect = self._read(f)
        # get the exit code of child process
        exitCode = os.waitpid(pid, 0)[1]
        output += 'Exit code is: %d\n' % exitCode
        # need to properly close the file handler
        os.close(f)
        return output

    def cmd(self, c):
        (pid, f) = self.run_cmd(c)
        return self.ssh_results(pid, f)

    def push(self, src, dst):
        s = os.stat(src)
        if stat.S_ISDIR(s[stat.ST_MODE]):
            (pid, f) = self.push_dir(src, dst)
        else:
            (pid, f) = self.push_file(src, dst)
        return self.ssh_results(pid, f)
