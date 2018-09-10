#
#
#  BLIS    
#  An object-based framework for developing high-performance BLAS-like
#  libraries.
#
#  Copyright (C) 2014, The University of Texas at Austin
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#   - Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   - Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   - Neither the name of The University of Texas at Austin nor the names
#     of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#

#
# fragment.mk 
#
# This is an automatically-generated makefile fragment and will likely get
# overwritten or deleted if the user is not careful. Modify at your own risk.
#

# These two mmakefile variables need to be set in order for the recursive
# include process to work!
CURRENT_DIR_NAME := src
CURRENT_SUB_DIRS := 

# Source files local to this fragment
LOCAL_SRC_FILES  := cblas_caxpy.c cblas_ccopy.c cblas_cdotc_sub.c cblas_cdotu_sub.c cblas_cgbmv.c cblas_cgemm.c cblas_cgemv.c cblas_cgerc.c cblas_cgeru.c cblas_chbmv.c cblas_chemm.c cblas_chemv.c cblas_cher2.c cblas_cher2k.c cblas_cher.c cblas_cherk.c cblas_chpmv.c cblas_chpr2.c cblas_chpr.c cblas_cscal.c cblas_csscal.c cblas_cswap.c cblas_csymm.c cblas_csyr2k.c cblas_csyrk.c cblas_ctbmv.c cblas_ctbsv.c cblas_ctpmv.c cblas_ctpsv.c cblas_ctrmm.c cblas_ctrmv.c cblas_ctrsm.c cblas_ctrsv.c cblas_dasum.c cblas_daxpy.c cblas_dcopy.c cblas_ddot.c cblas_dgbmv.c cblas_dgemm.c cblas_dgemv.c cblas_dger.c cblas_dnrm2.c cblas_drot.c cblas_drotg.c cblas_drotm.c cblas_drotmg.c cblas_dsbmv.c cblas_dscal.c cblas_dsdot.c cblas_dspmv.c cblas_dspr2.c cblas_dspr.c cblas_dswap.c cblas_dsymm.c cblas_dsymv.c cblas_dsyr2.c cblas_dsyr2k.c cblas_dsyr.c cblas_dsyrk.c cblas_dtbmv.c cblas_dtbsv.c cblas_dtpmv.c cblas_dtpsv.c cblas_dtrmm.c cblas_dtrmv.c cblas_dtrsm.c cblas_dtrsv.c cblas_dzasum.c cblas_dznrm2.c cblas_globals.c cblas_icamax.c cblas_idamax.c cblas_isamax.c cblas_izamax.c cblas_sasum.c cblas_saxpy.c cblas_scasum.c cblas_scnrm2.c cblas_scopy.c cblas_sdot.c cblas_sdsdot.c cblas_sgbmv.c cblas_sgemm.c cblas_sgemv.c cblas_sger.c cblas_snrm2.c cblas_srot.c cblas_srotg.c cblas_srotm.c cblas_srotmg.c cblas_ssbmv.c cblas_sscal.c cblas_sspmv.c cblas_sspr2.c cblas_sspr.c cblas_sswap.c cblas_ssymm.c cblas_ssymv.c cblas_ssyr2.c cblas_ssyr2k.c cblas_ssyr.c cblas_ssyrk.c cblas_stbmv.c cblas_stbsv.c cblas_stpmv.c cblas_stpsv.c cblas_strmm.c cblas_strmv.c cblas_strsm.c cblas_strsv.c cblas_xerbla.c cblas_zaxpy.c cblas_zcopy.c cblas_zdotc_sub.c cblas_zdotu_sub.c cblas_zdscal.c cblas_zgbmv.c cblas_zgemm.c cblas_zgemv.c cblas_zgerc.c cblas_zgeru.c cblas_zhbmv.c cblas_zhemm.c cblas_zhemv.c cblas_zher2.c cblas_zher2k.c cblas_zher.c cblas_zherk.c cblas_zhpmv.c cblas_zhpr2.c cblas_zhpr.c cblas_zscal.c cblas_zswap.c cblas_zsymm.c cblas_zsyr2k.c cblas_zsyrk.c cblas_ztbmv.c cblas_ztbsv.c cblas_ztpmv.c cblas_ztpsv.c cblas_ztrmm.c cblas_ztrmv.c cblas_ztrsm.c cblas_ztrsv.c

# Add the fragment's local source files to the _global_variable_ variable.
MK_FRAME_SRC += $(addprefix $(PARENT_PATH)/$(CURRENT_DIR_NAME)/, $(LOCAL_SRC_FILES))




# -----------------------------------------------------------------------------
# NOTE: The code below is generic and should remain in all fragment.mk files!
# -----------------------------------------------------------------------------

# Add the current fragment to the global list of fragments so the top-level
# Makefile knows which directories are participating in the build.
FRAGMENT_DIR_PATHS  += $(PARENT_PATH)/$(CURRENT_DIR_NAME)

# Recursively descend into other subfragments' local makefiles and include them.
ifneq ($(strip $(CURRENT_SUB_DIRS)),)
key                 := $(key).x
stack_$(key)        := $(PARENT_PATH)
PARENT_PATH         := $(PARENT_PATH)/$(CURRENT_DIR_NAME)
FRAGMENT_SUB_DIRS   := $(addprefix $(PARENT_PATH)/, $(CURRENT_SUB_DIRS))
-include  $(addsuffix /$(FRAGMENT_MK), $(FRAGMENT_SUB_DIRS))
PARENT_PATH         := $(stack_$(key))
key                 := $(basename $(key))
endif
