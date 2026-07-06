
#ai generated
def parse_vpd(data: bytes) -> dict:
    """Parse a PCI VPD blob into {keyword: value}.
 
    'Name' is the product string; 'PN' the part number; 'SN' the serial.
    """
    fields, i = {}, 0
    while i < len(data):
        tag = data[i]
        if tag == 0x78:                      # end tag
            break
        if tag & 0x80:                       # large resource tag
            length = data[i + 1] | (data[i + 2] << 8)
            payload = data[i + 3:i + 3 + length]
            if tag == 0x82:                  # product name string
                fields["Name"] = payload.decode("ascii", "replace").strip()
            elif tag == 0x90:                # VPD-R: 2-char keyword + len + value
                j = 0
                while j + 3 <= len(payload):
                    kw = payload[j:j + 2].decode("ascii", "replace")
                    klen = payload[j + 2]
                    val = payload[j + 3:j + 3 + klen].decode("ascii", "replace").strip()
                    fields[kw] = val
                    j += 3 + klen
            i += 3 + length
        else:                                # small resource tag
            i += 1 + (tag & 0x07)
    return fields
