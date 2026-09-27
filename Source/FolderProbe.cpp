#include "FolderProbe.h"

#include <chrono>
#include <future>
#include <memory>
#include <thread>

#if JUCE_WINDOWS
 #ifndef NOMINMAX
  #define NOMINMAX
 #endif
 #ifndef WIN32_LEAN_AND_MEAN
  #define WIN32_LEAN_AND_MEAN
 #endif
 #include <windows.h>
#endif

bool isReachableFolder(const juce::File& dir, int timeoutMs)
{
    // Neither test touches the network: a UNC path is recognised by its prefix, and
    // isOnHardDisk() only asks Windows what kind of drive the letter is.
    const bool isLocal = ! dir.getFullPathName().startsWith("\\\\") && dir.isOnHardDisk();

    if (isLocal)
        return dir.isDirectory();

    auto result = std::make_shared<std::promise<bool>>();
    auto answer = result->get_future();
    std::thread probe;

    try
    {
        probe = std::thread([dir, result] { result->set_value(dir.isDirectory()); });
    }
    catch (...)
    {
        return false; // no thread to spare: treat the folder as missing rather than risk a freeze
    }

    const bool inTime = answer.wait_for(std::chrono::milliseconds(timeoutMs)) == std::future_status::ready;

    // Abort a stalled network request so the helper finishes now rather than whenever
    // Windows gives up. It is always joined, never left running, in case the host unloads
    // the plugin soon after.
    while (answer.wait_for(std::chrono::milliseconds(inTime ? 0 : 50)) != std::future_status::ready)
    {
       #if JUCE_WINDOWS
        CancelSynchronousIo(probe.native_handle());
       #endif
    }

    probe.join();
    return inTime && answer.get();
}
