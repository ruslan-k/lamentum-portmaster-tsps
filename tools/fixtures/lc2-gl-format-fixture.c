/* Self-authored driver for the pure GLES upload-triple mapper.
 * stdin: one case per line, "api_major srgb_ext source_srgb upload_type".
 * stdout: one JSON object per line. Refusals carry no format fields at all, so
 * a caller cannot mistake a failed mapping for a usable GL triple.
 */
#include <stdio.h>
#include <stdlib.h>
#include "lc2_gl_format.h"

int main(void) {
    unsigned api_major, srgb_ext, source_srgb, upload_type;
    while (scanf("%u %u %u %u", &api_major, &srgb_ext, &source_srgb, &upload_type) == 4) {
        struct lc2_gl_upload out;
        out.internal = out.external = out.type = 0;
        enum lc2_gl_format_status status =
            lc2_gl_upload_format(api_major, srgb_ext, source_srgb, upload_type, &out);
        if (status == LC2_GL_FORMAT_OK)
            printf("{\"status\":%d,\"internal\":%u,\"external\":%u,\"type\":%u}\n",
                   (int)status, out.internal, out.external, out.type);
        else
            printf("{\"status\":%d}\n", (int)status);
    }
    return 0;
}
