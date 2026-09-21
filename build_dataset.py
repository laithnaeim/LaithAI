import json

roblox_dataset = [
    {
        "prompt": "Create a secure DataStore system that saves and loads a player's Coins and Level. It should handle failures with pcall, retry failed requests, autosave periodically, and save when the server shuts down.",
        "completion": r"""local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")
local RunService = game:GetService("RunService")

local playerStore = DataStoreService:GetDataStore("PlayerData_v1")

local DEFAULT_DATA = {
	Coins = 0,
	Level = 1,
}

local AUTOSAVE_INTERVAL = 60
local MAX_RETRIES = 3
local sessionData = {}

local function createDefaultData()
	return {
		Coins = DEFAULT_DATA.Coins,
		Level = DEFAULT_DATA.Level,
	}
end

local function loadData(player)
	local key = "Player_" .. player.UserId
	local data

	for attempt = 1, MAX_RETRIES do
		local success, result = pcall(function()
			return playerStore:GetAsync(key)
		end)

		if success then
			data = result or createDefaultData()
			break
		end

		if attempt < MAX_RETRIES then
			task.wait(attempt * 2)
		end
	end

	if not data then
		player:Kick("Your data could not be loaded. Please rejoin.")
		return
	end

	sessionData[player] = data
	return data
end

local function saveData(player)
	local data = sessionData[player]
	if not data then
		return false
	end

	local key = "Player_" .. player.UserId

	for attempt = 1, MAX_RETRIES do
		local success = pcall(function()
			playerStore:UpdateAsync(key, function()
				return data
			end)
		end)

		if success then
			return true
		end

		if attempt < MAX_RETRIES then
			task.wait(attempt * 2)
		end
	end

	return false
end

Players.PlayerAdded:Connect(function(player)
	loadData(player)
end)

Players.PlayerRemoving:Connect(function(player)
	saveData(player)
	sessionData[player] = nil
end)

task.spawn(function()
	while true do
		task.wait(AUTOSAVE_INTERVAL)
		for player in pairs(sessionData) do
			task.defer(saveData, player)
		end
	end
end)

game:BindToClose(function()
	if RunService:IsStudio() then
		task.wait(2)
	end

	local remaining = 0
	for player in pairs(sessionData) do
		remaining += 1
		task.spawn(function()
			saveData(player)
			remaining -= 1
		end)
	end

	while remaining > 0 do
		task.wait()
	end
end)"""
    },
    {
        "prompt": "Create a leaderstats system that gives every player Coins, Level, and Kills when they join. Make the values visible on the Roblox leaderboard and clean up any temporary references when players leave.",
        "completion": r"""local Players = game:GetService("Players")

Players.PlayerAdded:Connect(function(player)
	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats"
	leaderstats.Parent = player

	local coins = Instance.new("IntValue")
	coins.Name = "Coins"
	coins.Value = 0
	coins.Parent = leaderstats

	local level = Instance.new("IntValue")
	level.Name = "Level"
	level.Value = 1
	level.Parent = leaderstats

	local kills = Instance.new("IntValue")
	kills.Name = "Kills"
	kills.Value = 0
	kills.Parent = leaderstats
end)

Players.PlayerRemoving:Connect(function(player)
	local leaderstats = player:FindFirstChild("leaderstats")
	if leaderstats then
		leaderstats:Destroy()
	end
end)"""
    },
    {
        "prompt": "Create a server-side raycast weapon that fires from a RemoteEvent. It should raycast from the player's character toward a target position, ignore the shooter's character, detect humanoids, and apply 25 damage.",
        "completion": r"""local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local fireEvent = ReplicatedStorage:WaitForChild("FireWeapon")
local DAMAGE = 25
local MAX_DISTANCE = 500

fireEvent.OnServerEvent:Connect(function(player, targetPosition)
	if typeof(targetPosition) ~= "Vector3" then
		return
	end

	local character = player.Character
	if not character then
		return
	end

	local head = character:FindFirstChild("Head")
	if not head then
		return
	end

	local direction = targetPosition - head.Position
	if direction.Magnitude <= 0 then
		return
	end

	if direction.Magnitude > MAX_DISTANCE then
		direction = direction.Unit * MAX_DISTANCE
	end

	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = {character}
	params.IgnoreWater = true

	local result = workspace:Raycast(head.Position, direction, params)
	if not result then
		return
	end

	local model = result.Instance:FindFirstAncestorOfClass("Model")
	local humanoid = model and model:FindFirstChildOfClass("Humanoid")

	if humanoid and humanoid.Health > 0 then
		humanoid:TakeDamage(DAMAGE)
	end
end)"""
    },
    {
        "prompt": "Create a TweenService script that smoothly opens a GUI frame from the center by scaling it from 0 to 1. Include an OpenPanel function and prevent multiple tweens from running at the same time.",
        "completion": r"""local TweenService = game:GetService("TweenService")

local panel = script.Parent
local scale = panel:FindFirstChildOfClass("UIScale") or Instance.new("UIScale")
scale.Parent = panel

local OPEN_INFO = TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out)
local isAnimating = false

local function OpenPanel()
	if isAnimating then
		return
	end

	isAnimating = true
	panel.Visible = true
	scale.Scale = 0

	local tween = TweenService:Create(scale, OPEN_INFO, {Scale = 1})
	tween:Play()
	tween.Completed:Wait()
	isAnimating = false
end

OpenPanel()"""
    },
    {
        "prompt": "Create a UI button animation where the button grows slightly when the mouse enters, returns to normal when the mouse leaves, and shrinks briefly when clicked. Use TweenService and avoid conflicting animations.",
        "completion": r"""local TweenService = game:GetService("TweenService")

local button = script.Parent

local normalSize = button.Size
local hoverSize = UDim2.new(normalSize.X.Scale * 1.05, normalSize.X.Offset, normalSize.Y.Scale * 1.05, normalSize.Y.Offset)
local pressedSize = UDim2.new(normalSize.X.Scale * 0.95, normalSize.X.Offset, normalSize.Y.Scale * 0.95, normalSize.Y.Offset)

local tweenInfo = TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local activeTween

local function tweenTo(size)
	if activeTween then
		activeTween:Cancel()
	end

	activeTween = TweenService:Create(button, tweenInfo, {Size = size})
	activeTween:Play()
end

button.MouseEnter:Connect(function()
	tweenTo(hoverSize)
end)

button.MouseLeave:Connect(function()
	tweenTo(normalSize)
end)

button.Activated:Connect(function()
	tweenTo(pressedSize)
	task.wait(0.1)
	tweenTo(normalSize)
end)"""
    },
    {
        "prompt": "Create a round timer script for a TextLabel that counts down from 60 to 0, formats the text to show double digits, and loops continuously using task.spawn.",
        "completion": r"""local Players = game:GetService("Players")

local label = script.Parent
local ROUND_LENGTH = 60

local function runRound()
	for remaining = ROUND_LENGTH, 0, -1 do
		label.Text = string.format("Time: %02d", remaining)
		task.wait(1)
	end

	label.Text = "Round Complete!"
	task.wait(3)
end

task.spawn(function()
	while label.Parent do
		runRound()
	end
end)"""
    }
]

def generate_jsonl_file(output_filename="roblox_training_data.jsonl"):
    with open(output_filename, 'w', encoding='utf-8') as f:
        for entry in roblox_dataset:
            f.write(json.dumps(entry) + '\n')
    print(f"Successfully generated {output_filename} with {len(roblox_dataset)} training examples!")

if __name__ == '__main__':
    generate_jsonl_file()
