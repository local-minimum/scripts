import re
from optparse import OptionParser as opt

prsr = opt()
prsr.add_option("-i", "--input", dest="input_file", metavar="FILE", help="Input pass.analaysis to patch")
prsr.add_option("-g", "--grayScale", dest="gray_scale", metavar="STRING", help="WITHIN QUOTATION: New grayscale to patch with EXAMPLE: \"\'grayscale_values\': [230.0, 206.0, 193.0, 177.0, 164.0, 151.0, 136.0, 126.0, 114.0, 103.0, 93.0, 83.0, 74.0, 65.0, 56.0, 49.0, 43.0, 35.0, 29.0, 25.0, 21.0, 19.0, 16.0]\"")
prsr.add_option("-o", "--output", dest="out", metavar="FILE", help="Output file, overwrites old by default")

options, args = prsr.parse_args()

def check_params(options):
	
    if options.out == None:
        options.out = options.input_file
    if re.match(r"grayscale_values\':\s\[(.+)\],", options.gray_scale) == None:
        quit("ERROR:Grayscale seem to be of wrong format!")

class gray_scale_patcher():
	
    def __init__(self):
        pass
		
    def patch(self, input_file, new_gs, output):

        PASS_ANALYSIS = self.parser(input_file)
	new_gs = str(new_gs) + str(",")
        for i in xrange(1, len(PASS_ANALYSIS)):
            p = re.compile(r"\'grayscale_values\':\s\[(.+)\],")
            PASS_ANALYSIS[i] = p.sub(new_gs, PASS_ANALYSIS[i])
        self.writer(PASS_ANALYSIS, output)	
	
    def writer(self, PASS_ANALYSIS, output):
		
        fh = open(output, "w")
        for line in PASS_ANALYSIS:
           fh.write(line)
				
    def parser(self, input_file):
		
        with open(input_file, "r") as pass_analysis:
            PASS_ANALYSIS = pass_analysis.readlines()
        return PASS_ANALYSIS
	
if __name__ == "__main__":
    patch = gray_scale_patcher()
    patch.patch(options.input_file, options.gray_scale, options.out)	
