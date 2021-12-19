# Copyright (c) 2021 Itz-fork
# Part of: Nexa-Userbot

import os

from pyrogram import filters
from pyrogram.types import Message
from nexa_userbot import NEXAUB, CMD_HELP
from nexa_userbot.core.main_cmd import nexaub_on_cmd, e_or_r, nexaub_on_cf
from nexa_userbot.core.nexaub_database.nexaub_db_conf import set_custom_var, get_custom_var
from nexa_userbot.core.nexaub_database.nexaub_db_pm import add_approved_user, rm_approved_user, check_user_approved
from nexa_userbot.helpers.pyrogram_help import get_arg
from .telegraph import upload_to_tgraph
from config import Config


# Help
CMD_HELP.update(
    {
        "pmguard": f"""
**Pm Guard,**

  ✘ `enablepmg` - To Enable Pm Guard
  ✘ `disablepmg` - To Disable Pm Guard
  ✘ `approve` - To Approve a User to Pm
  ✘ `disapprove` - To Disapprove a User to Pm
  ✘ `setpmtxt` - To Set Custom Pm Guard Text
  ✘ `setpmpic` - To Set Custom Pm Guard Picture
  ✘ `setpmwarns` - To Set Custom Amount of Warns

**Example:**

  ✘ `approve`,
   ⤷ Send in a private chat, if a group reply to user's message = `{Config.CMD_PREFIX}approve`

  ✘ `disapprove`,
   ⤷ Send in a private chat, if a group reply to user's message = `{Config.CMD_PREFIX}disapprove`

  ✘ `setpmtxt`,
   ⤷ Send with text = `{Config.CMD_PREFIX}setpmtxt This is the Pm Guard Text`
   ⤷ Reply to a message = `{Config.CMD_PREFIX}setpmtxt`

  ✘ `setpmpic`,
   ⤷ Reply to a message = `{Config.CMD_PREFIX}setpmpic`

  ✘ `setpmwarns`,
   ⤷ Send with text = `{Config.CMD_PREFIX}setpmwarns 4`

"""
    }
)

mod_file = os.path.basename(__file__)

# Configs
PM_GUARD_WARNS_DB = {}
PM_GUARD_MSGS_DB = {}
DEFAULT_PM_TEXT = """
Because of the spam messages my master get all the time, he don't like to chat with "strangers" now!
So kindly please wait for his approval 🤗!
"""
BASE_PM_TEXT = """
**Heya 👋, This is PM Security of {} 👮!**

{}

`You have {}/{} of warns! Be careful, if you've exceeded warn limit you'll be blocked 🛑!`
"""
DEFAULT_PM_PIC = "cache/NEXAUB.png"
DEFAULT_PM_MESSAGE_LIMIT = 5


# Enable PM Guard
@nexaub_on_cmd(command="enablepmg", modlue=mod_file)
async def enable_pm_guard_nexaub(_, message: Message):
    pmg_emsg = await e_or_r(nexaub_message=message, msg_text="`Processing...`")
    is_already = await get_custom_var("ENABLE_PM_GUARD")
    if is_already:
        return await pmg_emsg.edit("`PM Guard is already enabled!`")
    await set_custom_var("ENABLE_PM_GUARD", True)
    await pmg_emsg.edit("**Successfully Enabled PM Guard!**")

# Disable PM Guard
@nexaub_on_cmd(command="disablepmg", modlue=mod_file)
async def disble_pm_guard_nexaub(_, message: Message):
    pmg_dmsg = await e_or_r(nexaub_message=message, msg_text="`Processing...`")
    is_already = await get_custom_var("ENABLE_PM_GUARD")
    if not is_already:
        return await pmg_dmsg.edit("`PM Guard isn't even enabled!`")
    await set_custom_var("ENABLE_PM_GUARD", False)
    await pmg_dmsg.edit("**Successfully Disabled PM Guard!**")

# Approve user
@nexaub_on_cmd(command="approve", modlue=mod_file)
async def approve_user_to_pm(_, message: Message):
    apprv_msg = await e_or_r(nexaub_message=message, msg_text="`Processing...`")
    chat_type = message.chat.type
    if chat_type in ["group", "supergroup"]:
        if not message.reply_to_message.from_user:
            return await apprv_msg.edit("`Reply to a user id to approve that user!`")
        user_id = message.reply_to_message.from_user.id
    elif chat_type == "private":
        user_id = message.chat.id
    else:
        return
    already_apprvd = await check_user_approved(user_id)
    if already_apprvd:
        return await apprv_msg.edit("`This user is already approved to PM!`")
    await add_approved_user(user_id)
    if user_id in PM_GUARD_WARNS_DB:
        PM_GUARD_WARNS_DB.pop(user_id)
    await apprv_msg.edit("**From now on, this user can PM my master!**")

# Disapprove user
@nexaub_on_cmd(command="disapprove", modlue=mod_file)
async def disapprove_user_to_pm(_, message: Message):
    dapprv_msg = await e_or_r(nexaub_message=message, msg_text="`Processing...`")
    chat_type = message.chat.type
    if chat_type in ["group", "supergroup"]:
        if not message.reply_to_message.from_user:
            return await dapprv_msg.edit("`Reply to a user id to disapprove that user!`")
        user_id = message.reply_to_message.from_user.id
    elif chat_type == "private":
        user_id = message.chat.id
    else:
        return
    already_apprvd = await check_user_approved(user_id)
    if not already_apprvd:
        return await dapprv_msg.edit("`This user isn't even approved to PM!`")
    await rm_approved_user(user_id)
    await dapprv_msg.edit("**From now on, this user can't PM my master!**")

# Set PM Guard text
@nexaub_on_cmd(command="setpmtxt", modlue=mod_file)
async def set_pm_guard_txt_nexaub(_, message: Message):
    st_pm_txt_msg = await e_or_r(nexaub_message=message, msg_text="`Processing...`")
    r_msg = message.reply_to_message
    args_txt = get_arg(message)
    if r_msg:
        if r_msg.text:
            pm_txt = r_msg.text
        else:
            return await st_pm_txt_msg.edit("`Reply to a text message!`")
    elif args_txt:
        pm_txt = args_txt
    else:
        return await st_pm_txt_msg.edit("`Reply to a text message or send this command with the text you want to set!`")
    await set_custom_var("CUSTOM_PM_TEXT", pm_txt)
    await st_pm_txt_msg.edit(f"**Successfully Added Custom PM Guard Text!** \n\n**New Message:** `{pm_txt}`")

# Set PM Guard pic
@nexaub_on_cmd(command="setpmpic", modlue=mod_file)
async def set_pm_guard_pic_nexaub(_, message: Message):
    st_pm_pic_msg = await e_or_r(nexaub_message=message, msg_text="`Processing...`")
    r_msg = message.reply_to_message
    if r_msg:
        if r_msg.photo:
            pm_pic = r_msg.download()
        if r_msg.animation:
            pm_pic = r_msg.download()
        else:
            return await st_pm_pic_msg.edit("`Reply to a picture or gif!`")
    else:
        return await st_pm_pic_msg.edit("`Reply to a picture or gif!`")
    pm_pic_link = await upload_to_tgraph(pm_pic)
    await set_custom_var("CUSTOM_PM_PIC", pm_pic_link)
    await st_pm_pic_msg.edit(f"**Successfully Added Custom PM Guard Pic!** \n\n**New Pic:** {pm_pic_link}")

# Set PM Guard warn limit
@nexaub_on_cmd(command="setpmwarns", modlue=mod_file)
async def set_pm_guard_warns_nexaub(_, message: Message):
    st_pm_warns_msg = await e_or_r(nexaub_message=message, msg_text="`Processing...`")
    args_txt = get_arg(message)
    if args_txt:
        if args_txt.isnumeric():
            pm_warns = int(args_txt)
        else:
            return await st_pm_warns_msg.edit(f"`Send this command with an integer!` \n\n**Ex:** `{Config.CMD_PREFIX}setpmwarns 4`")
    else:
        return await st_pm_warns_msg.edit(f"`Send this command with an integer!` \n\n**Ex:** `{Config.CMD_PREFIX}setpmwarns 4`")
    await set_custom_var("CUSTOM_PM_WARNS_LIMIT", pm_warns)
    await st_pm_warns_msg.edit(f"**Successfully Added Custom PM Guard Warn Limit to** `{args_txt}` *Warns!**")


# Custom handler to handle icoming pms
@nexaub_on_cf(
    (filters.private
    & filters.incoming
    & ~filters.me
    & ~filters.service
    & ~filters.edited
    & ~filters.bot),
    handler_group=-1
)
async def handle_pm_guard(_, message: Message):
    # Checking if pm guard is enabled
    is_pm_guard_enabled = await get_custom_var("ENABLE_PM_GUARD")
    if not is_pm_guard_enabled:
        return
    # User
    in_user = message.from_user
    in_user_id = in_user.id
    # Checking if user is approved to pm
    is_approved = await check_user_approved(in_user_id)
    if is_approved:
        return
    # Checking user's telegram status
    if in_user.is_fake or in_user.is_scam:
        await message.reply("`Damn looks like you're a spammer 🤔. Bye Bye!`")
        return await NEXAUB.block_user(in_user_id)
    if in_user.is_support or in_user.is_verified or in_user.is_self:
        return
    # Collecting Pm guard configs
    master = await NEXAUB.get_me()
    getc_pm_txt = await get_custom_var("CUSTOM_PM_TEXT")
    getc_pm_pic = await get_custom_var("CUSTOM_PM_PIC")
    getc_pm_warns = await get_custom_var("CUSTOM_PM_WARNS_LIMIT")
    custom_pm_txt = getc_pm_txt if getc_pm_txt else DEFAULT_PM_TEXT
    custom_pm_pic = getc_pm_pic if getc_pm_pic else DEFAULT_PM_PIC
    custom_pm_warns = getc_pm_warns if getc_pm_warns else DEFAULT_PM_MESSAGE_LIMIT
    # Checking user's warns
    if in_user_id in PM_GUARD_WARNS_DB:
        # Deleting old warn messages (Uses try except block cuz this is completely unwanted and in case of error process might be stopped)
        chat_id = message.chat.id
        try:
            if chat_id in PM_GUARD_MSGS_DB:
                msg = PM_GUARD_MSGS_DB[chat_id]
                await msg.delete()
        except:
            pass
        # Giving warnings
        PM_GUARD_WARNS_DB[in_user_id] += 1
        if PM_GUARD_WARNS_DB[in_user_id] >= custom_pm_warns:
            await message.reply(f"`That's it! I told you {custom_pm_warns} times, DO NOT pm my master and you didn't it! Anyway I've blocked you 😑!`")
            return await NEXAUB.block_user(in_user_id)
        else:
            rplied_msg = await message.reply_photo(photo=custom_pm_pic, caption=BASE_PM_TEXT.format(master.mention, custom_pm_txt, PM_GUARD_WARNS_DB[in_user_id], custom_pm_warns))
            PM_GUARD_MSGS_DB[chat_id] = rplied_msg
            return
    else:
        PM_GUARD_WARNS_DB[in_user_id] = 1
    # Logging details on the channel
    log_chnnel_id = await get_custom_var("LOG_CHANNEL_ID")
    copied = await message.copy(log_chnnel_id)
    await copied.reply(f"#Pm_Guard_Log \n\n**User:** {in_user.mention} \n**User ID: `{in_user_id}`")