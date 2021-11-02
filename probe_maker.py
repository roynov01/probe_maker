import tkinter as tk
from tkinter import filedialog
import NCBI
import tkinter.font as fnt
from tkinter import messagebox
import webbrowser
import pyperclip
from tkinter.scrolledtext import ScrolledText


DEFAULT_PATH = "C:\\Users"
DEFAULT_PATH2 = "C:\\Users"
LABEL_MAX_LEN = 4
UCSC_url = 'https://genome.ucsc.edu/'
BIOSEARCH_url = 'https://www.biosearchtech.com/support/tools/design-software/stellaris-probe-designer'
BLAST_url = 'http://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastn&BLAST_PROGRAMS=megaBlast&PAGE_TYPE=BlastSearch'
BIOSEARCH_INSTRUCTIONS = """# Log in\n# Go to Stellaris Probe Designer Access\n# Define probe: set name, gene name, \
organism,\nmasking level (usually 5 unless you have a short gene,\nthen you can lower it to 0)\n\
in probe number always insert a higher number\nthan what you want (usually 96)\n\
# Continue to the next stage
"""
BLAST_INSTRUCTIONS = """# upload FASTA file\n# Change database to Reference RNA sequences\n\
# Add organisms\n# BLAST\n# Download output as Hit Table (text)
"""
LEVEL = 16


class Probe:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap('rna.ico')
        self.root.title('probe maker for smFISH')
        self.root.geometry('1180x650')
        root.protocol("WM_DELETE_WINDOW", self.quit_attempt)
        root.configure(background='light blue')

        self.organism = ''
        self.directory = None
        self.messages = []
        self.name = ''
        self.matlab_command = ''

        # widgets:
        self.label_1 = tk.Label(self.root, text='Choose working directory: ', bg='light blue', justify='right',
                                width=28, height=3, relief='flat', anchor='e')
        self.label_2 = tk.Label(self.root, text='Choose organism: ', bg='light blue', justify='left', width=28,
                                height=3, relief='flat', anchor='e')
        self.label_3 = tk.Label(self.root, text='Insert gene name: ', bg='light blue', justify='left', width=28,
                                height=3, relief='flat', anchor='e')
        self.label_4 = tk.Label(self.root, text='Or search in UCSC: ', bg='light blue', justify='left', width=28,
                                height=3, relief='flat', anchor='e')
        self.label_5 = tk.Label(self.root, text='And insert refseq id: ', bg='light blue', justify='left', width=28,
                                height=3, relief='flat', anchor='e')
        self.label_6 = tk.Label(self.root, text='Find possible probes using: ', bg='light blue', justify='left',
                                width=28, height=3, relief='flat', anchor='e')
        self.label_7 = tk.Label(self.root, text='Copy the probes table here: ', bg='light blue', justify='left',
                                width=28, height=3, relief='flat', anchor='e')
        self.label_8 = tk.Label(self.root, text='Upload FASTA file to BLAST: \n(and save as', bg='light blue',
                                justify='left', width=28, height=3, relief='flat', anchor='e')
        self.label_9 = tk.Label(self.root, text='Run this command in MATLAB: ', bg='light blue', justify='left',
                                width=28, height=3, relief='flat', anchor='e')
        self.button_choose_dir = tk.Button(self.root, text='Choose working directory', fg='black', bg='tomato',
                                           width=36, height=1, activebackground='blue', relief='raised',
                                           command=self.choose_directory, state='normal', font=fnt.Font(size=20))
        self.button_mouse = tk.Button(self.root, text='Mouse', fg='black', bg='tomato', width=17, height=1,
                                      activebackground='blue', relief='raised', command=self.mouse,
                                      state='disabled', font=fnt.Font(size=20))
        self.button_human = tk.Button(self.root, text='Human', fg='black', bg='tomato', width=17, height=1,
                                      activebackground='blue', relief='raised', command=self.human, state='disabled',
                                      font=fnt.Font(size=20))
        self.label_updates = tk.Label(self.root, text='', bg='dodger blue', justify='left', width=42, height=38,
                                      relief='groove', anchor='w')
        self.entry_gene_name = tk.Entry(self.root, cursor='xterm', width=16, bg='white', bd=5, font=('Verdana', 20))
        self.button_accept_name = tk.Button(self.root, text='Accept', fg='black', bg='slateBlue1', width=17, height=1,
                                            activebackground='blue', relief='raised', command=self.accept_name,
                                            state='disabled', font=fnt.Font(size=20))
        self.button_ucsc = tk.Button(self.root, fg='blue', bg='tomato', state='normal', width=36, height=1,
                                     cursor="hand2", text='Open UCSC - genome browser', activebackground='blue',
                                     relief='raised', command=lambda: self.open_url(UCSC_url),
                                     font=fnt.Font(size=20, underline=True))
        self.entry_gene_id = tk.Entry(self.root, cursor='xterm', width=16, bg='white', bd=5, font=('Verdana', 20))
        self.button_accept_id = tk.Button(self.root, text='Accept', fg='black', bg='slateBlue1', width=17, height=1,
                                          activebackground='blue', relief='raised', command=self.accept_id,
                                          state='disabled', font=fnt.Font(size=20))
        self.button_biosearch = tk.Button(self.root, text='Open BIOSEARCH', fg='blue', bg='tomato', width=36, height=1,
                                          activebackground='blue', relief='raised', cursor="hand2",
                                          command=lambda: self.open_url(BIOSEARCH_url, BIOSEARCH_INSTRUCTIONS),
                                          state='normal', font=fnt.Font(size=20, underline=True))
        self.entry_probes = ScrolledText(self.root, cursor='xterm', width=32, height=3, bg='white', bd=5)
        self.button_accept_probes = tk.Button(self.root, text='Create Fasta', fg='black', bg='slateBlue1',
                                              width=17, height=1, activebackground='blue', relief='raised',
                                              command=self.accept_probes, state='disabled', font=fnt.Font(size=20))
        self.button_blast = tk.Button(self.root, text='Open BLAST', fg='blue', bg='tomato', width=17, height=1,
                                      activebackground='blue', relief='raised', cursor="hand2",
                                      command=lambda: self.open_url(BLAST_url, BLAST_INSTRUCTIONS),
                                      state='normal', font=fnt.Font(size=20, underline=True))
        self.button_open_blast_output = tk.Button(self.root, text='Open BLAST output', fg='black', bg='slateBlue1',
                                                  width=17, height=1, activebackground='blue', relief='raised',
                                                  command=self.open_blast_output, state='disabled',
                                                  font=fnt.Font(size=20))
        self.button_matlab_command = tk.Button(self.root, text='Copy command to clipboard', fg='black', bg='wheat2',
                                               width=36, height=1, activebackground='blue', relief='raised',
                                               command=self.copy_command, state='disabled', font=fnt.Font(size=20))
        self.button_reset = tk.Button(self.root, text='Reset', fg='black', bg='green', width=36, height=1,
                                      activebackground='blue', relief='raised', command=self.reset, state='normal',
                                      font=fnt.Font(size=20))

        # functional placements:
        self.button_choose_dir.grid(column=1, row=0, columnspan=2, padx=10, pady=3)
        self.button_mouse.grid(column=1, row=1, padx=10, pady=3)
        self.button_human.grid(column=2, row=1, padx=10, pady=3)
        self.label_updates.grid(column=4, row=0, rowspan=9, padx=10, pady=3)
        self.label_1.grid(column=0, row=0, padx=10, pady=3)
        self.label_2.grid(column=0, row=1, padx=10, pady=3)
        self.label_3.grid(column=0, row=2, padx=10, pady=3)
        self.label_4.grid(column=0, row=3, padx=10, pady=3)
        self.label_5.grid(column=0, row=4, padx=10, pady=3)
        self.label_6.grid(column=0, row=5, padx=10, pady=3)
        self.label_7.grid(column=0, row=6, padx=10, pady=3)
        self.label_8.grid(column=0, row=7, padx=10, pady=3)
        self.label_9.grid(column=0, row=8, padx=10, pady=3)
        self.entry_gene_name.grid(column=1, row=2, padx=10, pady=3)
        self.button_accept_name.grid(column=2, row=2, padx=10, pady=3)
        self.button_ucsc.grid(column=1, row=3, columnspan=2, padx=10, pady=3)
        self.entry_gene_id.grid(column=1, row=4, padx=10, pady=3)
        self.button_accept_id.grid(column=2, row=4, padx=10, pady=3)
        self.button_biosearch.grid(column=1, row=5, columnspan=2, padx=10, pady=3)
        self.entry_probes.grid(column=1, row=6, padx=10, pady=3)
        self.button_accept_probes.grid(column=2, row=6, padx=10, pady=3)
        self.button_blast.grid(column=1, row=7, padx=10, pady=3)
        self.button_open_blast_output.grid(column=2, row=7, padx=10, pady=3)
        self.button_matlab_command.grid(column=1, row=8, columnspan=2, padx=10, pady=3)
        self.button_reset.grid(column=1, row=9, columnspan=2, padx=10, pady=3)

        self.display("[APPLICATION STARTED SUCCESSFULLY]", False)

    def quit_attempt(self, reset=False):
        """quit the apps"""
        word = "restart" if reset else "quit"
        if messagebox.askokcancel(word, f"Are you sure you want to {word}?"):
            print('[APPLICATION CLOSED]')
            if reset:
                self.__init__(self.root)
            else:
                self.root.destroy()

    def choose_directory(self):
        """pops a dialog to open a folder and changes the availability of some of the buttons"""
        directory = filedialog.askdirectory(initialdir=DEFAULT_PATH)
        if not directory:
            return
        self.display(f'[DIRECTORY CHOSEN]\n{directory}', True)
        self.directory = directory
        self.enable_button(self.button_accept_id, "slateBlue1")
        self.enable_button(self.button_accept_probes, "slateBlue1")
        self.enable_button(self.button_open_blast_output, "slateBlue1")
        self.button_choose_dir['bg'] = 'saddle brown'
        if not self.organism:
            self.enable_button(self.button_mouse)
            self.enable_button(self.button_human)

    @staticmethod
    def disable_button(button, color="saddle brown"):
        button['state'] = "disabled"
        button['bg'] = color

    @staticmethod
    def enable_button(button, color="tomato"):
        button['state'] = "normal"
        button['bg'] = color

    def display(self, message: str, new_line=True):
        """
        displays updates at the label_updates and prints them
        :param message: str to be displayed and printed
        :param new_line: bool. add '\n' before the string
        """
        if len(self.messages) > LABEL_MAX_LEN:
            del self.messages[0]
        if new_line:
            message = '\n' + message
        print(message)
        if self.messages and message == self.messages[-1]:  # prevent duplicate messages
            return
        self.messages.append(message)
        self.label_updates['text'] = '\n'.join(self.messages)

    def open_url(self, url, message=''):
        """opens a url in the default system browser, and displays an update"""
        webbrowser.open_new(url)
        if message:
            self.display(f'[OPENING] {url}\n\n'+message)
            if url == BLAST_url:
                pyperclip.copy(self.directory)
            return
        self.display(f'[OPENING] {url}')

    def mouse(self):
        """changes the organism choice"""
        self.organism = "mouse"
        self.display(f'[ORGANISM CHOSEN] {self.organism}')
        self.enable_button(self.button_human)
        self.enable_button(self.button_accept_name, 'slateBlue1')
        self.disable_button(self.button_mouse)

    def human(self):
        """changes the organism choice"""
        self.organism = "human"
        self.display(f'[ORGANISM CHOSEN] {self.organism}')
        self.enable_button(self.button_accept_name, 'slateBlue1')
        self.enable_button(self.button_mouse)
        self.disable_button(self.button_human)

    def accept_name(self):
        """will show all possible refseqs (non-predicted), alongside the length of the sequence"""
        gene = self.entry_gene_name.get()
        if not gene:  # empty entry
            return
        try:
            possible_refseqs = NCBI.get_possible_refseqs(gene, self.organism)
            if possible_refseqs:
                refseqs_dict = NCBI.all_possible_refseqs(possible_refseqs)
                lengths = NCBI.refseqs_length(refseqs_dict)
                s = NCBI.str_of_refseqs_length(lengths)
                self.display("[POSSIBLE GENE IDs]\n" + s)
                pyperclip.copy(NCBI.shortest_refseq(lengths))
        except ValueError:
            self.display(f'[NO REFSEQS FOUND FOR THE GENE] {gene}')

    def accept_id(self):
        """will find the sequence of the refseq based on the gene id (example: NM_001271552.1)
        will create a sequence file and copy the sequence to the clipboard"""
        gene = self.entry_gene_id.get()
        try:
            sequence = str(NCBI.get_sequence(gene))
            self.name = self.entry_gene_name.get()
            if not self.name:
                self.name = gene
            with open(f"{self.directory}\\{self.name}_refseq.txt", "w") as file:
                file.write(sequence)
            pyperclip.copy(sequence)
            self.display("[REFSEQ FILE SAVED AND COPIED TO CLIPBOARD]")
        except ValueError:
            self.display(f'[GENE NOT FOUND] {gene}')


    def accept_probes(self):
        """take the data (matrix,  looks like: 1  cggaaaggcactgtctatgg  152  55.0%\n...) from the entry """
        if not self.name:
            self.name = self.entry_gene_name.get()
        probes = self.entry_probes.get("1.0", tk.END)
        if probes != ' ':  # if empty entry
            self.save_probes_files(probes)

    def save_probes_files(self, probes):
        """
        will create 3 files in the chosen directory:
        1. x_probes_raw.txt - has the raw matrix data
        2. probes.txt - has only the sequences (2nd column from the matrix)
        3. probes.fasta - same as 2, but with a line separating each probe sequence
        """
        probes_detailed = probes.split('\n')
        probes = [line.split('\t') for line in probes_detailed]
        index = 1
        with open(f"{self.directory}\\{self.name}_probes.txt", "w") as txt, \
            open(f"{self.directory}\\{self.name}_probes.fasta", "w") as fasta, \
                open(f"{self.directory}\\{self.name}_probes_raw.txt", "w") as raw_txt:
            try:
                for line in probes:
                    if len(line) == 5:  # ['', '1', 'cggaaaggcactgtctatgg', '152', '55.0%']
                        sequence = line[2]
                        # whole_line = '\t'.join(line[0:])
                    elif len(line) == 4:  # ['1', 'cggaaaggcactgtctatgg', '152', '55.0%']
                        sequence = line[1]
                        # whole_line = '\t'.join(line)
                    elif len(line) == 1:  # ['']
                        continue
                    txt.write(sequence + '\n')
                    raw_txt.write('\t'.join(line) + '\n')
                    fasta.write(f'>probe{index}\n{sequence}\n')
                    index += 1
                self.display('[FASTA FILE HAS BEEN CREATED]')
            except:
                self.display("[THE PROBE FORMAT ISN'T CORRECT]")

    def open_blast_output(self):
        """will copy the file to the chosen directory (with a new name) and will create the command that can be
        used in MATLAB in order to create a heatmap of the probes"""
        if not self.name:
            self.name = self.entry_gene_name.get()
        init_path = DEFAULT_PATH2
        original_file = filedialog.askopenfile(initialdir=init_path)
        if not original_file or not original_file.name.endswith('.txt'):
            return
        copied_file = f"{self.directory}\\{self.name}_httbl.txt"
        with open(copied_file, "w") as f:
            for line in original_file:
                # if not line.startswith('#'):
                f.write(line)
            self.display('[FILE HAS BEEN SAVED TO DIRECTORY]')
        original_file.close()
        self.display('[FILE HAS BEEN SAVED TO DIRECTORY]')
        self.matlab_command = f"detect_blast_multiple_hits_new('{copied_file}',{LEVEL})"
        self.button_matlab_command.configure(bg='gold', state='normal')
        self.copy_command()

    def copy_command(self):
        """copies the MATLAB final command to the clipboard"""
        pyperclip.copy(self.matlab_command)
        self.display(f'[MATLAB COMMAND COPIED TO CLIPBOARD]')

    def reset(self):
        self.quit_attempt(True)


if __name__ == "__main__":
    window = tk.Tk()
    Probe(window)
    window.mainloop()
