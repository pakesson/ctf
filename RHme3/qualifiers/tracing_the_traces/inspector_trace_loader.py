import numpy
import struct

# Adapted from https://github.com/Riscure/Jlsca/blob/master/src/trs-inspector.jl
# (Licensed under GPLv3)

# Tags
TRS_NUMBER_OF_TRACES = 0x41
TRS_NUMBER_OF_SAMPLES_PER_TRACE = 0x42
TRS_SAMPLE_CODING = 0x43
TRS_DATA_SPACE = 0x44
TRS_TITLE_SPACE = 0x45
TRS_DESCRIPTION = 0x47
TRS_TRACE_BLOCK = 0x5f

# Tag lengths
TRS_NUMBER_OF_TRACES_LENGTH = 4
TRS_NUMBER_OF_SAMPLES_PER_TRACE_LENGTH = 4
TRS_SAMPLE_CODING_LENGTH = 1
TRS_DATA_SPACE_LENGTH = 2
TRS_TITLE_SPACE_LENGTH = 1

# Types
TRS_TYPE_BYTE = 0x01
TRS_TYPE_SHORT = 0x02
TRS_TYPE_INT = 0x02
TRS_TYPE_FLOAT = 0x14

def load_trs(filename):
    with open(filename, "rb") as f:
        title_space = 0
        number_of_traces = 0
        data_space = 0
        sample_space = 0
        sample_type = TRS_TYPE_BYTE
        number_of_samples_per_trace = 0
        trace_block_position = 0

        done = False
        while not done:
            tag = struct.unpack('B', f.read(1))[0]
            length = struct.unpack('B', f.read(1))[0]

            if length & 0x80 == 0x80:
                length = 0
                # TODO: Read and unpack all bytes at once?
                for n in range(length & 0x7f):
                    length += struct.unpack('B', f.read(1))[0] << 8*n

            if tag == TRS_TRACE_BLOCK:
                # The trace block starts here
                if f.seekable():
                    trace_block_position = f.tell()
                done = True
            elif tag == TRS_TITLE_SPACE and length == TRS_TITLE_SPACE_LENGTH:
                buf = f.read(1)
                title_space = struct.unpack('B', buf)[0]
            elif tag == TRS_NUMBER_OF_TRACES and length == TRS_NUMBER_OF_TRACES_LENGTH:
                buf = f.read(4)
                number_of_traces = struct.unpack('<I', buf)[0]
            elif tag == TRS_DATA_SPACE and length == TRS_DATA_SPACE_LENGTH:
                buf = f.read(2)
                data_space = struct.unpack('<H', buf)[0]
            elif tag == TRS_NUMBER_OF_SAMPLES_PER_TRACE and length == TRS_NUMBER_OF_SAMPLES_PER_TRACE_LENGTH:
                buf = f.read(4)
                number_of_samples_per_trace = struct.unpack('<I', buf)[0]
            elif tag == TRS_SAMPLE_CODING and length == TRS_SAMPLE_CODING_LENGTH:
                sample_coding = struct.unpack('B', f.read(1))[0]
                if sample_coding == TRS_TYPE_BYTE:
                    sample_type = TRS_TYPE_BYTE
                    sample_space = 1
                elif sample_coding == TRS_TYPE_SHORT:
                    sample_type = TRS_TYPE_SHORT
                    sample_space = 2
                elif sample_coding == TRS_TYPE_INT:
                    sample_type = TRS_TYPE_INT
                    sample_space = 4
                elif sample_coding == TRS_TYPE_FLOAT:
                    sample_type = TRS_TYPE_FLOAT
                    sample_space = 4
                else:
                    # TODO: Throw exception
                    print("Unknown sample type {}".format(sample_coding))
            else:
                # TODO: Throw exception instead?
                #print("Could not parse tag {} with length {}".format(tag, length))
                f.read(length)

        traces = []
        data = []
        for n in range(number_of_traces):
            # Get in position
            position = trace_block_position + n * (title_space + data_space + number_of_samples_per_trace * sample_space)
            if f.tell() != position:
                f.seek(position)
            f.read(title_space)

            # Read data
            if data_space > 0:
                buf = f.read(data_space)
                buf = struct.unpack('<{}B'.format(data_space), buf)
                data.append(numpy.array(buf, dtype=numpy.uint8))

            # Read samples
            buf = f.read(sample_space * number_of_samples_per_trace)
            samples = 0
            dtype = numpy.uint8
            if sample_type == TRS_TYPE_BYTE:
                dtype = numpy.uint8
                samples = struct.unpack('<{}B'.format(number_of_samples_per_trace), buf)
            elif sample_type == TRS_TYPE_SHORT:
                dtype = numpy.int16
                samples = struct.unpack('<{}h'.format(number_of_samples_per_trace), buf)
            elif sample_coding == TRS_TYPE_INT:
                dtype = numpy.uint32
                samples = struct.unpack('<{}I'.format(number_of_samples_per_trace), buf)
            elif sample_coding == TRS_TYPE_FLOAT:
                dtype = numpy.float
                samples = struct.unpack('<{}f'.format(number_of_samples_per_trace), buf)

            traces.append(numpy.array(samples, dtype=dtype))

    if data:
        data = numpy.vstack(data)

    return (numpy.vstack(traces), data)