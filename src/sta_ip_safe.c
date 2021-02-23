/**
 * @file sta_ip_safe.c
 * @author TheSomeMan
 * @date 2020-08-26
 * @copyright Ruuvi Innovations Ltd, license BSD-3-Clause.
 */

#include "sta_ip_safe.h"
#include "os_mutex.h"
#include "sta_ip_unsafe.h"
#define LOG_LOCAL_LEVEL LOG_LEVEL_DEBUG
#include "log.h"

static const char TAG[] = "wifi_manager";

static os_mutex_t        g_sta_ip_safe_mutex;
static os_mutex_static_t g_sta_ip_safe_mutex_mem;

STA_IP_SAFE_STATIC
os_mutex_t
sta_ip_safe_mutex_get(void)
{
    return g_sta_ip_safe_mutex;
}

STA_IP_SAFE_STATIC
bool
sta_ip_safe_lock(const TickType_t ticks_to_wait)
{
    os_mutex_t h_mutex = sta_ip_safe_mutex_get();
    if (NULL == h_mutex)
    {
        LOG_ERR("Mutex is not initialized");
        return false;
    }
    return os_mutex_lock_with_timeout(h_mutex, ticks_to_wait);
}

STA_IP_SAFE_STATIC
void
sta_ip_safe_unlock(void)
{
    os_mutex_t h_mutex = sta_ip_safe_mutex_get();
    if (NULL == h_mutex)
    {
        LOG_ERR("Mutex is not initialized");
        return;
    }
    os_mutex_unlock(h_mutex);
}

bool
sta_ip_safe_init(void)
{
    if (NULL != sta_ip_safe_mutex_get())
    {
        LOG_ERR("Mutex was already initialized");
        return false;
    }
    g_sta_ip_safe_mutex = os_mutex_create_static(&g_sta_ip_safe_mutex_mem);
    sta_ip_unsafe_init();
    return sta_ip_safe_reset(portMAX_DELAY);
}

void
sta_ip_safe_deinit(void)
{
    const bool flag_locked = sta_ip_safe_lock(portMAX_DELAY);
    sta_ip_unsafe_deinit();
    if (flag_locked)
    {
        sta_ip_safe_unlock();
    }
    os_mutex_delete(&g_sta_ip_safe_mutex);
}

bool
sta_ip_safe_set(const sta_ip_address_t ip, const TickType_t ticks_to_wait)
{
    if (!sta_ip_safe_lock(ticks_to_wait))
    {
        LOG_WARN("%s: Timeout waiting mutex", __func__);
        return false;
    }
    sta_ip_unsafe_set(ip);
    const char *ip_str = sta_ip_unsafe_get_str();
    LOG_INFO("Set STA IP String to: %s", ip_str);
    sta_ip_safe_unlock();
    return true;
}

bool
sta_ip_safe_reset(const TickType_t ticks_to_wait)
{
    return sta_ip_safe_set((sta_ip_address_t)0, ticks_to_wait);
}

sta_ip_string_t
sta_ip_safe_get(TickType_t ticks_to_wait)
{
    if (!sta_ip_safe_lock(ticks_to_wait))
    {
        LOG_WARN("%s: Timeout waiting mutex", __func__);
        const sta_ip_string_t ip_str = { 0 };
        return ip_str;
    }
    const sta_ip_string_t ip_str = sta_ip_unsafe_get_copy();
    sta_ip_safe_unlock();
    return ip_str;
}

sta_ip_address_t
sta_ip_safe_conv_str_to_ip(const char *p_ip_addr_str)
{
    return sta_ip_unsafe_conv_str_to_ip(p_ip_addr_str);
}
