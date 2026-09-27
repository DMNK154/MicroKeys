#pragma once

#include <juce_core/juce_core.h>

// Whether dir is an existing folder, without freezing the caller for long. A folder on a
// local disk is checked directly. One on a network share (or another non-local drive) is
// checked on a helper thread: Windows can take 20-60 s to report that a share is
// unreachable, so after timeoutMs the check is abandoned and the folder counts as missing.
bool isReachableFolder(const juce::File& dir, int timeoutMs);
