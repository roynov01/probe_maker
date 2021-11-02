from Bio import Entrez, SeqIO
import mygene


STOP_CODONS = {"TAA", "TAG", "TGA"}
Entrez.email = 'roy.novoselsky@mail.huji.ac.il'


def get_possible_refseqs(name, organism):
    """
    :param name: str, name of gene
    :param organism: str. 'mouse', 'human'...
    :return: list of ids
    """
    if not name:
        return
    details = mygene.MyGeneInfo()
    translate = details.querymany(name, scopes='symbol', fields="all", species=organism)
    try:
        possible_refseqs = translate[0]["refseq"]["rna"]
        return possible_refseqs
    except KeyError:
        raise ValueError(f"no gene named [{name}] found!")


def get_sequence(id):
    """
    :param id: str, id of gene (NM_xxxxxx or NR_xxxxx)
    :return: str, the sequence of the gene
    """
    if id.startswith("XM") or id.startswith("XR"):
        return
    try:
        handle = Entrez.efetch(db='nuccore', id=id, rettype='fasta')
        record = SeqIO.read(handle, 'fasta')
        return record.seq
    except:
        raise ValueError(f"no gene with the id [{id}] found!")


def shortest_refseq(possible_refseqs):
    return min(possible_refseqs, key=lambda x: x[1])[0]


def all_possible_refseqs(possible_refseqs: list):
    """
    :param possible_refseqs: list of strings.
    :return: dict, {gene_id : gene_sequence}
    """
    refseqs_dict = {}
    for refseq in possible_refseqs:
        full_seq = get_sequence(refseq)
        if full_seq:
            refseqs_dict[refseq] = full_seq
    return refseqs_dict


def refseqs_length(refseqs_dict):
    """return list of the refseqs, in increasing order by their sequence length"""
    lengths = []
    for key in refseqs_dict:
        sequence = refseqs_dict[key]
        lengths.append([key, len(sequence)])
    return sorted(lengths, key=lambda x: x[1])


def str_of_refseqs_length(lengths):
    """returns a string containing all the refseqs ids with their length.
    example: NM_001271552.1\t999\nNM_001271552.2\t... """
    string = ''
    for id, length in lengths:
        string = f'{string}{id}\t{str(length)}\n'
    return string


if __name__ == "__main__":
    # gene = "Aire"
    # organism = "mouse"
    #
    # possible_refseqs = get_possible_refseqs(gene, organism)
    #
    #
    # refseqs_dict = all_possible_refseqs(possible_refseqs)
    # # x = shortest_refseq(refseqs_dict.items())
    # # print(x)
    # lengths = refseqs_length(refseqs_dict)
    # print(f'shortest: {shortest_refseq(lengths)}')
    # s = str_of_refseqs_length(lengths)
    # print('*****\n', s)

    # print(get_sequence("NM_001271552.1"))
    pass
