return {
	on = {
	    devices = { 'Humi2 - Уровень воды' }, 
	    timer = {'at 23:00', 'at 06:00'}
	},
	execute = function(domoticz, item)
	    local minLevel = domoticz.variables('minWaterLevel').value
	    local power = domoticz.devices('Humi2 - Питание')
	    local val = domoticz.devices('Humi2 - Уровень воды').nValue
	    local mode = domoticz.devices('Humi2 - Режим работы') --mode.level

	    if (item.isTimer) then
            local Time = require('Time')
            local t = Time()
            
            if (t.matchesRule('at 23:00-05:59')) then
                mode.switchSelector(10)
            else
                mode.switchSelector(0)
            end
            
        elseif (item.isDevice) then 
    	    if (val < minLevel and power.state=='On') then
    	        domoticz.log("Low level! Power off", domoticz.LOG_INFO)
    	        power.switchOff()
            end
            
    	    if (val >= minLevel and power.state=='Off') then
    	        domoticz.log("Normal level! Power on!", domoticz.LOG_INFO)
    	        power.switchOn()
            end
        end

	end
}
