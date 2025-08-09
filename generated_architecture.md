# 代码架构设计文档：Creating Data Sources for Master Data of Characteristic "Product"

## 1. 总体架构分层

### 架构选择理由
采用分层架构（Layered Architecture）设计，原因如下：
1. 业务流程涉及数据建模、对象创建和属性配置等多个关注点，分层可清晰分离职责
2. 数据仓库工作台操作需要与底层存储解耦
3. 未来可能需要支持多种前端（Web/CLI）访问方式

### 架构层次图
```
┌─────────────────────┐
│   API/Application   │ ◄─ REST/GraphQL接口
├─────────────────────┤
│      Services       │ ◄─ 业务流程封装
├─────────────────────┤
│ Data Access Layer   │ ◄─ 持久化操作
├─────────────────────┤
│   Domain Models     │ ◄─ 核心业务对象
└─────────────────────┘
```

## 2. 各层详细模块与代码结构

### 2.1 领域模型层 (Domain Models)
```java
// SAP BW核心领域对象
class InfoProvider {
    String technicalName;
    String description;
    List<Dimension> dimensions;
    List<Characteristic> characteristics;
}

class Dimension {
    String name;
    List<Characteristic> characteristics;
    List<NavigationAttribute> navigationAttributes;
}

class Characteristic {
    String technicalName;
    String description;
    boolean isShippedObject;
}

class NavigationAttribute {
    String technicalName;
    boolean isActive;
}
```

### 2.2 数据访问层 (DAL)

#### InfoProviderRepository.java
```java
public interface InfoProviderRepository {
    InfoProvider findByName(String technicalName);
    InfoProvider save(InfoProvider provider);
    Dimension addDimension(String providerName, Dimension dimension);
    void assignCharacteristic(String providerName, String dimensionName, 
                            Characteristic characteristic);
    void activateNavigationAttribute(String providerName, String dimensionName,
                                   String attributeName);
}
```

#### SAPBWTemplateRepository.java
```java
public class SAPBWTemplateRepository implements InfoProviderRepository {
    // 实现基于SAP BW工作台的CRUD操作
    // 包含与SAP BW后端的连接管理
}
```

### 2.3 服务层 (Service Layer)

#### InfoProviderService.java
```java
public class InfoProviderService {
    private final InfoProviderRepository repository;
    
    public InfoProvider createInfoCube(String technicalName, String description) {
        InfoProvider cube = new InfoProvider(technicalName, description);
        return repository.save(cube);
    }
    
    public Dimension createDimension(String providerName, String dimensionName) {
        Dimension dim = new Dimension(dimensionName);
        return repository.addDimension(providerName, dim);
    }
    
    public void assignCharacteristic(String providerName, String dimensionName,
                                   String characteristicName) {
        Characteristic char = new Characteristic(characteristicName);
        repository.assignCharacteristic(providerName, dimensionName, char);
    }
    
    public void activateNavigationAttribute(String providerName, String dimensionName,
                                        String attributeName) {
        repository.activateNavigationAttribute(providerName, dimensionName, attributeName);
    }
}
```

### 2.4 应用接口层 (API Layer)

#### InfoProviderController.java
```java
@RestController
@RequestMapping("/api/infoproviders")
public class InfoProviderController {
    private final InfoProviderService service;
    
    @PostMapping("/cubes")
    public ResponseEntity<InfoProvider> createInfoCube(
            @RequestBody CreateCubeRequest request) {
        InfoProvider cube = service.createInfoCube(
            request.getTechnicalName(), 
            request.getDescription());
        return ResponseEntity.created(URI.create("/cubes/" + cube.getTechnicalName()))
                           .body(cube);
    }
    
    @PostMapping("/{providerName}/dimensions")
    public ResponseEntity<Dimension> addDimension(
            @PathVariable String providerName,
            @RequestBody AddDimensionRequest request) {
        Dimension dim = service.createDimension(providerName, request.getName());
        return ResponseEntity.ok(dim);
    }
    
    @PutMapping("/{providerName}/dimensions/{dimensionName}/characteristics")
    public ResponseEntity<Void> assignCharacteristic(
            @PathVariable String providerName,
            @PathVariable String dimensionName,
            @RequestBody AssignCharacteristicRequest request) {
        service.assignCharacteristic(providerName, dimensionName, 
                                  request.getCharacteristicName());
        return ResponseEntity.noContent().build();
    }
    
    @PatchMapping("/{providerName}/dimensions/{dimensionName}/attributes/{attributeName}")
    public ResponseEntity<Void> activateAttribute(
            @PathVariable String providerName,
            @PathVariable String dimensionName,
            @PathVariable String attributeName) {
        service.activateNavigationAttribute(providerName, dimensionName, attributeName);
        return ResponseEntity.noContent().build();
    }
}
```

## 3. 业务流程到代码架构的映射

### LTL公式步骤与代码实现对应表

| 业务流程步骤 | 对应代码组件 | 方法/API端点 |
|--------------|--------------|--------------|
| 1. 进入Modeling功能区域 | 前端实现 | N/A |
| 2. 选择Info Provider | InfoProviderRepository | findByName() |
| 3. 创建Info Cube | InfoProviderService | createInfoCube() |
| 4. 输入技术名称和描述 | CreateCubeRequest DTO | POST /api/infoproviders/cubes |
| 5. 选择Standard Info Cube类型 | InfoProviderService.createInfoCube() | 硬编码在服务中 |
| 6. 创建新维度 | InfoProviderService | createDimension() |
| 7. 添加Product维度 | DimensionService | POST /api/infoproviders/{name}/dimensions |
| 8. 添加Sales Organization维度 | DimensionService | 同上 |
| 9. 选择Info Object Catalog | InfoObjectCatalogRepository | 单独组件 |
| 10. 选择特征目录 | CharacteristicService | 单独组件 |
| 11. 分配特征到维度 | InfoProviderService | assignCharacteristic() |
| 12. 选择Direct Input | CharacteristicService | 单独组件 |
| 13. 输入销售文档特征 | AssignCharacteristicRequest | PUT /characteristics |
| 14. 激活导航属性 | InfoProviderService | activateNavigationAttribute() |

### 一致性保障机制
1. **严格命名对应**：技术名称如"ZD_SALES"直接映射到代码中的technicalName字段
2. **操作原子性**：每个业务流程步骤对应一个独立的服务方法
3. **状态管理**：InfoProvider聚合根确保维度、特征的状态一致性
4. **审计追踪**：可通过API调用的HTTP方法(POST/PUT/PATCH)反映业务流程意图

## 4. 扩展设计考虑

### 异常处理策略
```java
@ControllerAdvice
public class SAPBWExceptionHandler {
    @ExceptionHandler(InfoProviderNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(InfoProviderNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                           .body(new ErrorResponse(ex.getMessage()));
    }
    
    @ExceptionHandler(DuplicateDimensionException.class)
    public ResponseEntity<ErrorResponse> handleConflict(DuplicateDimensionException ex) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
                           .body(new ErrorResponse(ex.getMessage()));
    }
}
```

### 性能优化建议
1. 对InfoProvider实现缓存装饰器(Caching Decorator)
2. 批量处理维度创建请求
3. 对导航属性激活实现异步处理

## 5. 架构验证指标

1. **业务流程覆盖率**：100%步骤可映射到具体代码组件
2. **接口幂等性**：PUT/PATCH操作满足LTL公式要求
3. **可测试性**：各服务方法可独立进行单元测试
4. **可扩展性**：新增维度类型或特征类型无需修改核心架构